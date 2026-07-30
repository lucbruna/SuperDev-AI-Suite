from __future__ import annotations

import asyncio
import json
import os
from collections.abc import AsyncIterator
from typing import Any

import httpx

from .base_provider import (
    BaseLLMProvider,
    ProviderError,
    ProviderErrorCode,
    PricingRow,
    StreamDelta,
    _exponential_backoff,
    _is_retryable,
    count_tokens,
)


DEEPSEEK_PRICING: dict[str, PricingRow] = {
    "deepseek-chat": PricingRow(0.00014, 0.00028),
    "deepseek-coder": PricingRow(0.00014, 0.00028),
    "deepseek-reasoner": PricingRow(0.00055, 0.00219),
}


class DeepSeekProvider(BaseLLMProvider):
    """DeepSeek provider using the OpenAI-compatible API.

    Supports:
    - Chat (deepseek-chat, deepseek-coder, deepseek-reasoner)
    - Streaming (SSE)
    - Function calling
    - FIM (Fill-in-the-Middle) via deepseek-coder
    - Automatic retry with exponential backoff
    - Rate limiting
    """

    BASE_URL = "https://api.deepseek.com"

    def __init__(
        self,
        model: str = "deepseek-chat",
        api_key: str = "",
        base_url: str = "",
        max_retries: int = 3,
        requests_per_minute: int = 500,
    ) -> None:
        super().__init__(name="deepseek", model=model)
        self._api_key = api_key or os.getenv("DEEPSEEK_API_KEY", "")
        self._base_url = base_url or os.getenv("DEEPSEEK_BASE_URL") or self.BASE_URL
        self._max_retries = max_retries
        self._pricing = DEEPSEEK_PRICING
        self._http_client: httpx.AsyncClient | None = None
        if self._api_key:
            self.set_rate_limit(requests_per_minute)

    # ── Client ──────────────────────────────────────────────────────

    def _get_client(self) -> httpx.AsyncClient:
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(
                base_url=self._base_url,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                timeout=httpx.Timeout(120.0, connect=30.0),
            )
        return self._http_client

    # ── ILLMProvider ────────────────────────────────────────────────

    async def generate(self, prompt: str, **kwargs: Any) -> dict[str, Any]:
        return await self._execute_with_retry(self._generate, prompt, **kwargs)

    async def generate_stream(self, prompt: str, **kwargs: Any) -> AsyncIterator[dict[str, Any]]:
        async def _stream() -> AsyncIterator[dict[str, Any]]:
            attempt = 0
            while attempt <= self._max_retries:
                try:
                    await self._throttle()
                    async for chunk in self._stream_chunks(prompt, **kwargs):
                        yield chunk
                    break
                except ProviderError as e:
                    attempt += 1
                    if attempt > self._max_retries or not _is_retryable(e, self._retry_codes):
                        yield {"content": f"[{self._name} error: {e.message}]", "finish_reason": "error", "error": e.message}
                        break
                    retry_after = e.retry_after or _exponential_backoff(attempt - 1)
                    await asyncio.sleep(retry_after)
                except Exception as e:
                    pe = ProviderError.from_exception(e, self._name)
                    attempt += 1
                    if attempt > self._max_retries or not _is_retryable(pe, self._retry_codes):
                        yield {"content": f"[{self._name} error: {pe.message}]", "finish_reason": "error", "error": pe.message}
                        break
                    await asyncio.sleep(_exponential_backoff(attempt - 1))
        return _stream()

    async def validate(self, params: dict[str, Any]) -> bool:
        return True

    # ── Internal generation ─────────────────────────────────────────

    async def _generate(self, prompt: str, **kwargs: Any) -> dict[str, Any]:
        client = self._get_client()
        body = self._build_body(prompt, kwargs, stream=False)

        try:
            resp = await client.post("/chat/completions", json=body)
            data = self._handle_response(resp)
        except httpx.HTTPError as e:
            raise self._classify_error(e)

        choice = data["choices"][0]
        message = choice.get("message", {})
        content = message.get("content", "")
        tool_calls = message.get("tool_calls")

        pt = data.get("usage", {}).get("prompt_tokens", count_tokens(prompt))
        ct = data.get("usage", {}).get("completion_tokens", count_tokens(content))

        # DeepSeek reasoner sends reasoning_content
        reasoning = message.get("reasoning_content")

        result = {
            "content": content,
            "success": True,
            "finish_reason": choice.get("finish_reason", "stop"),
            **self._track_usage(pt, ct),
        }
        if tool_calls:
            result["tool_calls"] = [
                {"id": tc.get("id", ""), "type": "function", "function": tc.get("function", {})}
                for tc in tool_calls
            ]
        if reasoning:
            result["reasoning"] = reasoning
        return result

    async def _stream_chunks(self, prompt: str, **kwargs: Any) -> AsyncIterator[dict[str, Any]]:
        client = self._get_client()
        body = self._build_body(prompt, kwargs, stream=True)
        usage_info: dict[str, int] = {}

        try:
            async with client.stream("POST", "/chat/completions", json=body) as resp:
                if resp.status_code != 200:
                    error_text = await resp.aread()
                    raise ProviderError(
                        ProviderErrorCode.API_ERROR,
                        f"DeepSeek returned {resp.status_code}: {error_text.decode()[:200]}",
                        resp.status_code,
                        provider="deepseek",
                    )

                async for line in resp.aiter_lines():
                    if not line.strip():
                        continue
                    if line.startswith("data: "):
                        payload = line[6:]
                        if payload.strip() == "[DONE]":
                            continue
                        try:
                            data = json.loads(payload)
                        except json.JSONDecodeError:
                            continue

                        delta = data.get("choices", [{}])[0].get("delta", {})
                        finish = data.get("choices", [{}])[0].get("finish_reason")
                        content = delta.get("content", "")
                        reasoning = delta.get("reasoning_content", "")
                        tool_calls_delta = delta.get("tool_calls")

                        # Track usage from final chunk
                        if data.get("usage"):
                            usage_info = {
                                "prompt_tokens": data["usage"].get("prompt_tokens", 0),
                                "completion_tokens": data["usage"].get("completion_tokens", 0),
                                "total_tokens": data["usage"].get("total_tokens", 0),
                            }

                        chunk_result = {
                            "content": content,
                            "finish_reason": finish,
                            "delta": StreamDelta(content=content, finish_reason=finish, tool_calls=tool_calls_delta),
                            "usage": usage_info or None,
                        }
                        if reasoning:
                            chunk_result["reasoning"] = reasoning
                        yield chunk_result

        except httpx.HTTPError as e:
            raise self._classify_error(e)

        # Track final usage
        if usage_info:
            self._track_usage(usage_info.get("prompt_tokens", 0), usage_info.get("completion_tokens", 0))

    # ── Health ──────────────────────────────────────────────────────

    async def health(self) -> dict[str, Any]:
        import time as time_module
        start = time_module.monotonic()
        try:
            client = self._get_client()
            resp = await client.get("/models")
            elapsed = (time_module.monotonic() - start) * 1000
            if resp.status_code == 200:
                return {"status": "healthy", "latency_ms": round(elapsed, 1), "provider": "deepseek", "model": self._model}
            return {"status": "degraded", "latency_ms": round(elapsed, 1), "error": f"Status {resp.status_code}", "provider": "deepseek"}
        except Exception as e:
            elapsed = (time_module.monotonic() - start) * 1000
            return {"status": "unhealthy", "latency_ms": round(elapsed, 1), "error": str(e), "provider": "deepseek"}

    # ─── Model listing ────────────────────────────────────────────

    async def list_models(self) -> list[dict[str, Any]]:
        models = [
            {"id": "deepseek-chat", "name": "DeepSeek V3", "provider": "deepseek", "capabilities": ["chat", "tools"], "context_window": 65536, "max_tokens": 8192},
            {"id": "deepseek-coder", "name": "DeepSeek Coder", "provider": "deepseek", "capabilities": ["chat", "tools", "fim"], "context_window": 16384, "max_tokens": 4096},
            {"id": "deepseek-reasoner", "name": "DeepSeek R1", "provider": "deepseek", "capabilities": ["chat", "reasoning"], "context_window": 65536, "max_tokens": 8192},
        ]
        return models

    # ── Helpers ─────────────────────────────────────────────────────

    def _build_body(self, prompt: str, kwargs: dict[str, Any], stream: bool = False) -> dict[str, Any]:
        messages = self._build_messages(prompt, kwargs)
        body: dict[str, Any] = {
            "model": kwargs.get("model") or self._model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 4096),
            "stream": stream,
        }

        tools = kwargs.get("tools")
        if tools:
            body["tools"] = tools

        # DeepSeek-specific: prefix for FIM
        prefix = kwargs.get("prefix")
        suffix = kwargs.get("suffix")
        if prefix:
            body["prompt"] = prefix
            if suffix:
                body["suffix"] = suffix

        return body

    def _build_messages(self, prompt: str, kwargs: dict[str, Any]) -> list[dict[str, Any]]:
        messages = []
        system = kwargs.get("system")
        if system:
            messages.append({"role": "system", "content": system})

        chat_history = kwargs.get("messages", [])
        if chat_history:
            messages.extend(chat_history)

        messages.append({"role": "user", "content": prompt})
        return messages

    def _handle_response(self, resp: httpx.Response) -> dict[str, Any]:
        if resp.status_code == 200:
            return resp.json()
        try:
            error_data = resp.json()
            error_msg = error_data.get("error", {}).get("message", str(resp.text[:200]))
        except Exception:
            error_msg = resp.text[:200]
        raise ProviderError(
            ProviderErrorCode.API_ERROR,
            f"DeepSeek returned {resp.status_code}: {error_msg}",
            resp.status_code,
            provider="deepseek",
        )

    def _classify_error(self, exc: Exception) -> ProviderError:
        if isinstance(exc, ProviderError):
            return exc

        if isinstance(exc, httpx.TimeoutException):
            return ProviderError(ProviderErrorCode.TIMEOUT, str(exc), 408, provider="deepseek")

        msg = str(exc).lower()

        if "401" in msg or "unauthorized" in msg or "api key" in msg:
            return ProviderError(ProviderErrorCode.AUTH, str(exc), 401, provider="deepseek")
        if "429" in msg or "rate limit" in msg:
            return ProviderError(ProviderErrorCode.RATE_LIMIT, str(exc), 429, provider="deepseek")
        if "context" in msg and ("length" in msg or "exceed" in msg):
            return ProviderError(ProviderErrorCode.CONTEXT_LENGTH, str(exc), 400, provider="deepseek")
        if "500" in msg or "502" in msg or "503" in msg:
            return ProviderError(ProviderErrorCode.SERVER_ERROR, str(exc), 503, provider="deepseek")

        if isinstance(exc, httpx.HTTPStatusError):
            return ProviderError(ProviderErrorCode.API_ERROR, str(exc), exc.response.status_code, provider="deepseek")

        return ProviderError(ProviderErrorCode.API_ERROR, str(exc), 0, provider="deepseek")

    async def cleanup(self) -> None:
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

    def to_dict(self) -> dict[str, Any]:
        base = super().to_dict()
        base["api_key_set"] = bool(self._api_key)
        base["base_url"] = self._base_url
        return base
