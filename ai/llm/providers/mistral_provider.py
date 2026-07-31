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

MISTRAL_PRICING: dict[str, PricingRow] = {
    "mistral-large-latest": PricingRow(0.0005, 0.0015),
    "mistral-small-latest": PricingRow(0.0001, 0.0003),
    "open-mistral-nemo": PricingRow(0.0001, 0.0001),
    "codestral-latest": PricingRow(0.0002, 0.0006),
}


class MistralProvider(BaseLLMProvider):
    """Mistral provider using the OpenAI-compatible API.

    Supports:
    - Chat (mistral-large, mistral-small, open-mistral-nemo, codestral)
    - Streaming (SSE)
    - Function calling
    - Automatic retry + rate limiting
    """

    BASE_URL = "https://api.mistral.ai/v1"

    def __init__(
        self,
        model: str = "mistral-large-latest",
        api_key: str = "",
        base_url: str = "",
        max_retries: int = 3,
        requests_per_minute: int = 500,
    ) -> None:
        super().__init__(name="mistral", model=model)
        self._api_key = api_key or os.getenv("MISTRAL_API_KEY", "")
        self._base_url = base_url or os.getenv("MISTRAL_BASE_URL") or self.BASE_URL
        self._max_retries = max_retries
        self._pricing = MISTRAL_PRICING
        self._http_client: httpx.AsyncClient | None = None
        if self._api_key:
            self.set_rate_limit(requests_per_minute)

    def _get_client(self) -> httpx.AsyncClient:
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(
                base_url=self._base_url,
                headers={"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"},
                timeout=httpx.Timeout(120.0),
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
                        f"Mistral {resp.status_code}: {text.decode()[:200]}",
                        resp.status_code,
                        provider="mistral",
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
                "provider": "mistral",
                "model": self._model,
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "latency_ms": round((time_module.monotonic() - start) * 1000, 1),
                "error": str(e),
                "provider": "mistral",
            }

    async def list_models(self) -> list[dict[str, Any]]:
        return [
            {
                "id": "mistral-large-latest",
                "name": "Mistral Large",
                "provider": "mistral",
                "capabilities": ["chat", "tools", "json"],
                "context_window": 131072,
                "max_tokens": 8192,
            },
            {
                "id": "mistral-small-latest",
                "name": "Mistral Small",
                "provider": "mistral",
                "capabilities": ["chat", "tools"],
                "context_window": 32768,
                "max_tokens": 4096,
            },
            {
                "id": "open-mistral-nemo",
                "name": "Mistral Nemo",
                "provider": "mistral",
                "capabilities": ["chat", "tools"],
                "context_window": 32768,
                "max_tokens": 4096,
            },
            {
                "id": "codestral-latest",
                "name": "Codestral",
                "provider": "mistral",
                "capabilities": ["chat", "tools", "fim"],
                "context_window": 32768,
                "max_tokens": 8192,
            },
            {
                "id": "mistral-embed",
                "name": "Mistral Embed",
                "provider": "mistral",
                "capabilities": ["embedding"],
                "dimensions": 1024,
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
        response_format = kwargs.get("response_format")
        if response_format:
            body["response_format"] = response_format
        return body

    def _handle_response(self, resp: httpx.Response) -> dict[str, Any]:
        if resp.status_code == 200:
            return resp.json()
        raise ProviderError(
            ProviderErrorCode.API_ERROR,
            f"Mistral {resp.status_code}: {resp.text[:200]}",
            resp.status_code,
            provider="mistral",
        )

    def _classify_error(self, exc: Exception) -> ProviderError:
        if isinstance(exc, ProviderError):
            return exc
        if isinstance(exc, httpx.TimeoutException):
            return ProviderError(ProviderErrorCode.TIMEOUT, str(exc), 408, provider="mistral")
        msg = str(exc).lower()
        if "401" in msg or "unauthorized" in msg or "api key" in msg:
            return ProviderError(ProviderErrorCode.AUTH, str(exc), 401, provider="mistral")
        if "429" in msg or "rate limit" in msg:
            return ProviderError(ProviderErrorCode.RATE_LIMIT, str(exc), 429, provider="mistral")
        if isinstance(exc, httpx.HTTPStatusError):
            return ProviderError(ProviderErrorCode.API_ERROR, str(exc), exc.response.status_code, provider="mistral")
        return ProviderError(ProviderErrorCode.API_ERROR, str(exc), 0, provider="mistral")

    async def cleanup(self) -> None:
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

    def to_dict(self) -> dict[str, Any]:
        base = super().to_dict()
        base["api_key_set"] = bool(self._api_key)
        return base
