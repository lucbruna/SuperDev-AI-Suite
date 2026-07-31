from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncIterator
from typing import Any

from .base_provider import (
    OPENAI_PRICING,
    BaseLLMProvider,
    ProviderError,
    ProviderErrorCode,
    StreamDelta,
    _exponential_backoff,
    _is_retryable,
    count_tokens,
)


class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT provider using the official openai SDK.

    Supports:
    - Chat completions (gpt-4o, gpt-4o-mini, gpt-4, gpt-3.5-turbo)
    - Streaming
    - Vision (image URLs and base64)
    - Tool/function calling
    - Structured output (JSON mode / response_format)
    - Embeddings (text-embedding-3-small, text-embedding-3-large, text-embedding-ada-002)
    - Automatic retry with exponential backoff
    - Rate limiting
    """

    def __init__(
        self,
        model: str = "gpt-4o",
        api_key: str = "",
        base_url: str | None = None,
        organization: str | None = None,
        max_retries: int = 3,
        requests_per_minute: int = 500,
    ) -> None:
        super().__init__(name="openai", model=model)
        self._api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self._base_url = base_url or os.getenv("OPENAI_BASE_URL")
        self._organization = organization or os.getenv("OPENAI_ORG_ID")
        self._max_retries = max_retries
        self._pricing = OPENAI_PRICING
        self._client: Any = None
        self._aclient: Any = None
        if self._api_key:
            self.set_rate_limit(requests_per_minute)

    # ── Client ──────────────────────────────────────────────────────

    def _get_client(self):
        if self._aclient is None:
            try:
                from openai import AsyncOpenAI
                kwargs: dict[str, Any] = {"api_key": self._api_key, "max_retries": 0}
                if self._base_url:
                    kwargs["base_url"] = self._base_url
                if self._organization:
                    kwargs["organization"] = self._organization
                self._aclient = AsyncOpenAI(**kwargs)
            except ImportError:
                raise ProviderError(ProviderErrorCode.API_ERROR, "openai library required. pip install openai", provider="openai")
        return self._aclient

    # ── ILLMProvider ────────────────────────────────────────────────

    async def generate(self, prompt: str, **kwargs: Any) -> dict[str, Any]:
        return await self._execute_with_retry(self._generate, prompt, **kwargs)

    async def generate_stream(self, prompt: str, **kwargs: Any) -> AsyncIterator[dict[str, Any]]:
        async def _stream() -> AsyncIterator[dict[str, Any]]:
            attempt = 0
            while attempt <= self._max_retries:
                try:
                    await self._throttle()
                    raw_stream = await self._create_stream(prompt, **kwargs)
                    async for chunk in self._consume_stream(raw_stream):
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
        messages = self._build_messages(prompt, kwargs)
        model = kwargs.get("model") or self._model
        tools = kwargs.get("tools")
        response_format = kwargs.get("response_format")

        body: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 4096),
            "top_p": kwargs.get("top_p", 1.0),
        }
        if tools:
            body["tools"] = tools
            body["tool_choice"] = kwargs.get("tool_choice", "auto")
        if response_format:
            body["response_format"] = response_format

        try:
            resp = await client.chat.completions.create(**body)
        except Exception as e:
            raise self._classify_error(e)

        choice = resp.choices[0] if resp.choices else None
        if not choice:
            return {"content": "", "success": True, "finish_reason": "stop", **self._track_usage(0, 0)}

        message = choice.message
        content = message.content or ""
        tool_calls = None
        if message.tool_calls:
            tool_calls = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                }
                for tc in message.tool_calls
            ]

        pt = resp.usage.prompt_tokens if resp.usage else count_tokens(prompt)
        ct = resp.usage.completion_tokens if resp.usage else count_tokens(content)

        result = {
            "content": content,
            "success": True,
            "finish_reason": choice.finish_reason or "stop",
            **self._track_usage(pt, ct),
        }
        if tool_calls:
            result["tool_calls"] = tool_calls
        return result

    async def _create_stream(self, prompt: str, **kwargs: Any) -> Any:
        """Create and return the raw OpenAI stream. Returns an async iterable."""
        client = self._get_client()
        messages = self._build_messages(prompt, kwargs)
        model = kwargs.get("model") or self._model
        tools = kwargs.get("tools")
        response_format = kwargs.get("response_format")

        body: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 4096),
            "stream": True,
            "stream_options": {"include_usage": True},
        }
        if tools:
            body["tools"] = tools
        if response_format:
            body["response_format"] = response_format

        try:
            return await client.chat.completions.create(**body)
        except Exception as e:
            raise self._classify_error(e)

    async def _consume_stream(self, stream: Any) -> AsyncIterator[dict[str, Any]]:
        """Consume the raw OpenAI stream and yield dict chunks."""
        usage_info: dict[str, int] = {}
        async for chunk in stream:
            delta = chunk.choices[0].delta if chunk.choices else None
            finish = chunk.choices[0].finish_reason if chunk.choices else None

            content = delta.content if delta else ""
            tool_calls_delta = None
            if delta and delta.tool_calls:
                tool_calls_delta = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                    }
                    for tc in delta.tool_calls
                ]

            if chunk.usage:
                usage_info = {
                    "prompt_tokens": chunk.usage.prompt_tokens or 0,
                    "completion_tokens": chunk.usage.completion_tokens or 0,
                    "total_tokens": chunk.usage.total_tokens or 0,
                }

            yield {
                "content": content or "",
                "finish_reason": finish,
                "delta": StreamDelta(content=content or "", finish_reason=finish, tool_calls=tool_calls_delta),
                "usage": usage_info or None,
            }

        # Track final usage
        if usage_info:
            self._track_usage(usage_info.get("prompt_tokens", 0), usage_info.get("completion_tokens", 0))

    # ── Embeddings ──────────────────────────────────────────────────

    async def embeddings(self, texts: list[str], model: str = "text-embedding-3-small") -> list[list[float]]:
        client = self._get_client()
        try:
            resp = await client.embeddings.create(model=model, input=texts)
            return [item.embedding for item in resp.data]
        except Exception as e:
            raise self._classify_error(e)

    # ── Health ──────────────────────────────────────────────────────

    async def health(self) -> dict[str, Any]:
        import time as time_module
        start = time_module.monotonic()
        try:
            client = self._get_client()
            await client.models.list()
            elapsed = (time_module.monotonic() - start) * 1000
            return {"status": "healthy", "latency_ms": round(elapsed, 1), "provider": "openai", "model": self._model}
        except Exception as e:
            elapsed = (time_module.monotonic() - start) * 1000
            return {"status": "unhealthy", "latency_ms": round(elapsed, 1), "error": str(e), "provider": "openai"}

    # ─── Model listing ────────────────────────────────────────────

    async def list_models(self) -> list[dict[str, Any]]:
        models = [
            {"id": "gpt-4o", "name": "GPT-4o", "capabilities": ["chat", "vision", "tools", "json"], "context_window": 128000, "max_tokens": 16384},
            {"id": "gpt-4o-mini", "name": "GPT-4o Mini", "capabilities": ["chat", "vision", "tools", "json"], "context_window": 128000, "max_tokens": 16384},
            {"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "capabilities": ["chat", "vision", "tools", "json"], "context_window": 128000, "max_tokens": 4096},
            {"id": "gpt-4", "name": "GPT-4", "capabilities": ["chat", "tools"], "context_window": 8192, "max_tokens": 4096},
            {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "capabilities": ["chat", "tools"], "context_window": 16385, "max_tokens": 4096},
            {"id": "o1-mini", "name": "O1 Mini", "capabilities": ["chat"], "context_window": 128000, "max_tokens": 65536},
            {"id": "o1-preview", "name": "O1 Preview", "capabilities": ["chat"], "context_window": 128000, "max_tokens": 32768},
            {"id": "text-embedding-3-small", "name": "Embedding 3 Small", "capabilities": ["embedding"], "dimensions": 1536},
            {"id": "text-embedding-3-large", "name": "Embedding 3 Large", "capabilities": ["embedding"], "dimensions": 3072},
        ]
        return models

    # ── Vision helper ───────────────────────────────────────────────

    def build_vision_messages(self, text: str, image_url: str) -> list[dict[str, Any]]:
        """Build messages for vision requests."""
        return [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": text},
                    {"type": "image_url", "image_url": {"url": image_url, "detail": "auto"}},
                ],
            }
        ]

    # ── Helpers ─────────────────────────────────────────────────────

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

    def _classify_error(self, exc: Exception) -> ProviderError:
        msg = str(exc).lower()

        if "401" in msg or "unauthorized" in msg or "api key" in msg:
            return ProviderError(ProviderErrorCode.AUTH, str(exc), 401, provider="openai")
        if "429" in msg or "rate limit" in msg:
            return ProviderError(ProviderErrorCode.RATE_LIMIT, str(exc), 429, provider="openai")
        if "timeout" in msg or "timed out" in msg:
            return ProviderError(ProviderErrorCode.TIMEOUT, str(exc), 408, provider="openai")
        if "context_length_exceeded" in msg or "maximum context length" in msg:
            return ProviderError(ProviderErrorCode.CONTEXT_LENGTH, str(exc), 400, provider="openai")
        if "content_filter" in msg:
            return ProviderError(ProviderErrorCode.CONTENT_FILTER, str(exc), 400, provider="openai")

        # Check for OpenAI-specific error shapes
        status = getattr(exc, "status_code", 0) or getattr(exc, "http_status", 0)
        if status == 400:
            return ProviderError(ProviderErrorCode.INVALID_REQUEST, str(exc), 400, provider="openai")
        if status in (500, 502, 503):
            return ProviderError(ProviderErrorCode.SERVER_ERROR, str(exc), status, provider="openai")

        return ProviderError(ProviderErrorCode.API_ERROR, str(exc), status, provider="openai")

    async def cleanup(self) -> None:
        if self._aclient:
            await self._aclient.close()
            self._aclient = None

    def to_dict(self) -> dict[str, Any]:
        base = super().to_dict()
        base["api_key_set"] = bool(self._api_key)
        base["base_url"] = self._base_url
        return base
