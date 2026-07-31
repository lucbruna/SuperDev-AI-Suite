from __future__ import annotations

import asyncio
import json
import os
from collections.abc import AsyncIterator
from typing import Any

import httpx

from .base_provider import (
    BaseLLMProvider,
    PricingRow,
    ProviderError,
    ProviderErrorCode,
    StreamDelta,
    _exponential_backoff,
    _is_retryable,
    count_tokens,
)

GROQ_PRICING: dict[str, PricingRow] = {
    "llama-3.3-70b-versatile": PricingRow(0.00059, 0.00079),
    "llama-3.1-8b-instant": PricingRow(0.00005, 0.00008),
    "mixtral-8x7b-32768": PricingRow(0.00024, 0.00024),
    "gemma2-9b-it": PricingRow(0.00008, 0.00008),
}


class GroqProvider(BaseLLMProvider):
    """Groq provider using the OpenAI-compatible API.

    Supports:
    - Chat (llama-3.3-70b, llama-3.1-8b, mixtral, gemma2)
    - Streaming (SSE)
    - Function calling
    - Automatic retry + rate limiting
    """

    BASE_URL = "https://api.groq.com/openai/v1"

    def __init__(
        self,
        model: str = "llama-3.3-70b-versatile",
        api_key: str = "",
        base_url: str = "",
        max_retries: int = 3,
        requests_per_minute: int = 30,
    ) -> None:
        super().__init__(name="groq", model=model)
        self._api_key = api_key or os.getenv("GROQ_API_KEY", "")
        self._base_url = base_url or os.getenv("GROQ_BASE_URL") or self.BASE_URL
        self._max_retries = max_retries
        self._pricing = GROQ_PRICING
        self._http_client: httpx.AsyncClient | None = None
        if self._api_key:
            self.set_rate_limit(requests_per_minute)

    def _get_client(self) -> httpx.AsyncClient:
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(
                base_url=self._base_url,
                headers={"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"},
                timeout=httpx.Timeout(60.0),
            )
        return self._http_client

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
                        yield {
                            "content": f"[{self._name} error: {e.message}]",
                            "finish_reason": "error",
                            "error": e.message,
                        }
                        break
                    retry_after = e.retry_after or _exponential_backoff(attempt - 1)
                    await asyncio.sleep(retry_after)
                except Exception as e:
                    pe = ProviderError.from_exception(e, self._name)
                    attempt += 1
                    if attempt > self._max_retries or not _is_retryable(pe, self._retry_codes):
                        yield {
                            "content": f"[{self._name} error: {pe.message}]",
                            "finish_reason": "error",
                            "error": pe.message,
                        }
                        break
                    await asyncio.sleep(_exponential_backoff(attempt - 1))

        return _stream()

    async def validate(self, params: dict[str, Any]) -> bool:
        return True

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

        result = {
            "content": content,
            "success": True,
            "finish_reason": choice.get("finish_reason", "stop"),
            **self._track_usage(pt, ct),
        }
        if tool_calls:
            result["tool_calls"] = [
                {"id": tc["id"], "type": "function", "function": tc["function"]} for tc in tool_calls
            ]
        return result

    async def _stream_chunks(self, prompt: str, **kwargs: Any) -> AsyncIterator[dict[str, Any]]:
        client = self._get_client()
        body = self._build_body(prompt, kwargs, stream=True)
        usage_info: dict[str, int] = {}
        try:
            async with client.stream("POST", "/chat/completions", json=body) as resp:
                if resp.status_code != 200:
                    text = await resp.aread()
                    raise ProviderError(
                        ProviderErrorCode.API_ERROR,
                        f"Groq {resp.status_code}: {text.decode()[:200]}",
                        resp.status_code,
                        provider="groq",
                    )
                async for line in resp.aiter_lines():
                    if not line.strip() or not line.startswith("data: "):
                        continue
                    payload = line[6:].strip()
                    if payload == "[DONE]":
                        continue
                    try:
                        data = json.loads(payload)
                    except json.JSONDecodeError:
                        continue
                    delta = data.get("choices", [{}])[0].get("delta", {})
                    finish = data.get("choices", [{}])[0].get("finish_reason")
                    content = delta.get("content", "")
                    if data.get("usage"):
                        usage_info = {
                            "prompt_tokens": data["usage"].get("prompt_tokens", 0),
                            "completion_tokens": data["usage"].get("completion_tokens", 0),
                            "total_tokens": data["usage"].get("total_tokens", 0),
                        }
                    yield {
                        "content": content,
                        "finish_reason": finish,
                        "delta": StreamDelta(content=content, finish_reason=finish),
                        "usage": usage_info or None,
                    }
        except httpx.HTTPError as e:
            raise self._classify_error(e)
        if usage_info:
            self._track_usage(usage_info.get("prompt_tokens", 0), usage_info.get("completion_tokens", 0))

    async def health(self) -> dict[str, Any]:
        import time as time_module

        start = time_module.monotonic()
        try:
            resp = await self._get_client().get("/models")
            elapsed = (time_module.monotonic() - start) * 1000
            return {
                "status": "healthy" if resp.status_code == 200 else "degraded",
                "latency_ms": round(elapsed, 1),
                "provider": "groq",
                "model": self._model,
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "latency_ms": round((time_module.monotonic() - start) * 1000, 1),
                "error": str(e),
                "provider": "groq",
            }

    async def list_models(self) -> list[dict[str, Any]]:
        return [
            {
                "id": "llama-3.3-70b-versatile",
                "name": "Llama 3.3 70B",
                "provider": "groq",
                "capabilities": ["chat", "tools"],
                "context_window": 32768,
                "max_tokens": 8192,
            },
            {
                "id": "llama-3.1-8b-instant",
                "name": "Llama 3.1 8B Instant",
                "provider": "groq",
                "capabilities": ["chat", "tools"],
                "context_window": 131072,
                "max_tokens": 8192,
            },
            {
                "id": "mixtral-8x7b-32768",
                "name": "Mixtral 8x7B",
                "provider": "groq",
                "capabilities": ["chat", "tools"],
                "context_window": 32768,
                "max_tokens": 4096,
            },
            {
                "id": "gemma2-9b-it",
                "name": "Gemma 2 9B",
                "provider": "groq",
                "capabilities": ["chat"],
                "context_window": 8192,
                "max_tokens": 4096,
            },
        ]

    def _build_body(self, prompt: str, kwargs: dict[str, Any], stream: bool = False) -> dict[str, Any]:
        messages = []
        system = kwargs.get("system")
        if system:
            messages.append({"role": "system", "content": system})
        chat_history = kwargs.get("messages", [])
        if chat_history:
            messages.extend(chat_history)
        messages.append({"role": "user", "content": prompt})
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
        return body

    def _handle_response(self, resp: httpx.Response) -> dict[str, Any]:
        if resp.status_code == 200:
            return resp.json()
        raise ProviderError(
            ProviderErrorCode.API_ERROR,
            f"Groq {resp.status_code}: {resp.text[:200]}",
            resp.status_code,
            provider="groq",
        )

    def _classify_error(self, exc: Exception) -> ProviderError:
        if isinstance(exc, ProviderError):
            return exc
        if isinstance(exc, httpx.TimeoutException):
            return ProviderError(ProviderErrorCode.TIMEOUT, str(exc), 408, provider="groq")
        msg = str(exc).lower()
        if "401" in msg or "unauthorized" in msg or "api key" in msg:
            return ProviderError(ProviderErrorCode.AUTH, str(exc), 401, provider="groq")
        if "429" in msg or "rate limit" in msg:
            return ProviderError(ProviderErrorCode.RATE_LIMIT, str(exc), 429, provider="groq")
        if isinstance(exc, httpx.HTTPStatusError):
            return ProviderError(ProviderErrorCode.API_ERROR, str(exc), exc.response.status_code, provider="groq")
        return ProviderError(ProviderErrorCode.API_ERROR, str(exc), 0, provider="groq")

    async def cleanup(self) -> None:
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

    def to_dict(self) -> dict[str, Any]:
        base = super().to_dict()
        base["api_key_set"] = bool(self._api_key)
        return base
