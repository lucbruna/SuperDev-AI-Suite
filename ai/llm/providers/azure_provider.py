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

# Azure uses OpenAI pricing for equivalent models
AZURE_PRICING = OPENAI_PRICING


class AzureOpenAIProvider(BaseLLMProvider):
    """Azure OpenAI provider using the openai SDK with AsyncAzureOpenAI.

    Supports:
    - Chat completions (GPT-4o, GPT-4, GPT-3.5 via Azure deployments)
    - Streaming
    - Vision (image URLs)
    - Tool/function calling
    - Structured output (JSON mode / response_format)
    - Embeddings
    - API key or Entra ID (azure_ad_token) authentication
    - Automatic retry with exponential backoff
    - Rate limiting
    """

    def __init__(
        self,
        model: str = "gpt-4o",
        endpoint: str = "",
        api_key: str = "",
        api_version: str = "2024-10-21",
        azure_ad_token: str = "",
        max_retries: int = 3,
        requests_per_minute: int = 500,
    ) -> None:
        super().__init__(name="azure", model=model)
        self._original_model = model
        self._endpoint = endpoint or os.getenv("AZURE_OPENAI_ENDPOINT", "")
        self._api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY", "")
        self._api_version = api_version or os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")
        self._azure_ad_token = azure_ad_token or os.getenv("AZURE_OPENAI_AD_TOKEN", "")
        self._max_retries = max_retries
        self._pricing = AZURE_PRICING
        self._aclient: Any = None
        if self._api_key or self._azure_ad_token:
            self.set_rate_limit(requests_per_minute)

    # ── Client ──────────────────────────────────────────────────────

    def _get_client(self):
        if self._aclient is None:
            try:
                from openai import AsyncAzureOpenAI

                kwargs: dict[str, Any] = {
                    "azure_endpoint": self._endpoint,
                    "api_version": self._api_version,
                    "max_retries": 0,
                }
                if self._api_key:
                    kwargs["api_key"] = self._api_key
                elif self._azure_ad_token:
                    kwargs["azure_ad_token"] = self._azure_ad_token

                self._aclient = AsyncAzureOpenAI(**kwargs)
            except ImportError:
                raise ProviderError(
                    ProviderErrorCode.API_ERROR,
                    "openai library required. pip install openai",
                    provider="azure",
                )
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
        deployment = kwargs.get("deployment") or kwargs.get("model") or self._model
        tools = kwargs.get("tools")
        response_format = kwargs.get("response_format")

        body: dict[str, Any] = {
            "model": deployment,  # Azure uses deployment name as model
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
        client = self._get_client()
        messages = self._build_messages(prompt, kwargs)
        deployment = kwargs.get("deployment") or kwargs.get("model") or self._model
        tools = kwargs.get("tools")
        response_format = kwargs.get("response_format")

        body: dict[str, Any] = {
            "model": deployment,
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

    # ── Health ───────────────────────────────────────────────────────

    async def health(self) -> dict[str, Any]:
        import time as time_module

        start = time_module.monotonic()
        try:
            client = self._get_client()
            await client.models.list()
            elapsed = (time_module.monotonic() - start) * 1000
            return {"status": "healthy", "latency_ms": round(elapsed, 1), "provider": "azure", "model": self._model}
        except Exception as e:
            elapsed = (time_module.monotonic() - start) * 1000
            return {"status": "unhealthy", "latency_ms": round(elapsed, 1), "error": str(e), "provider": "azure"}

    # ── Models ───────────────────────────────────────────────────────

    async def list_models(self) -> list[dict[str, Any]]:
        return [
            {"id": "gpt-4o", "name": "GPT-4o", "capabilities": ["chat", "vision", "tools", "json"], "context_window": 128000},
            {"id": "gpt-4o-mini", "name": "GPT-4o Mini", "capabilities": ["chat", "vision", "tools", "json"], "context_window": 128000},
            {"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "capabilities": ["chat", "vision", "tools", "json"], "context_window": 128000},
            {"id": "gpt-4", "name": "GPT-4", "capabilities": ["chat", "tools"], "context_window": 8192},
            {"id": "gpt-35-turbo", "name": "GPT-3.5 Turbo", "capabilities": ["chat", "tools"], "context_window": 16385},
            {"id": "text-embedding-3-small", "name": "Embedding 3 Small", "capabilities": ["embedding"], "dimensions": 1536},
            {"id": "text-embedding-3-large", "name": "Embedding 3 Large", "capabilities": ["embedding"], "dimensions": 3072},
        ]

    # ── Vision ───────────────────────────────────────────────────────

    def build_vision_messages(self, text: str, image_url: str) -> list[dict[str, Any]]:
        return [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": text},
                    {"type": "image_url", "image_url": {"url": image_url, "detail": "auto"}},
                ],
            }
        ]

    # ── Helpers ──────────────────────────────────────────────────────

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

        if "401" in msg or "unauthorized" in msg or "api key" in msg or "access denied" in msg:
            return ProviderError(ProviderErrorCode.AUTH, str(exc), 401, provider="azure")
        if "429" in msg or "rate limit" in msg:
            return ProviderError(ProviderErrorCode.RATE_LIMIT, str(exc), 429, provider="azure")
        if "timeout" in msg or "timed out" in msg:
            return ProviderError(ProviderErrorCode.TIMEOUT, str(exc), 408, provider="azure")
        if "context_length_exceeded" in msg or "maximum context length" in msg:
            return ProviderError(ProviderErrorCode.CONTEXT_LENGTH, str(exc), 400, provider="azure")
        if "content_filter" in msg or "content management policy" in msg:
            return ProviderError(ProviderErrorCode.CONTENT_FILTER, str(exc), 400, provider="azure")
        if "deployment" in msg and "not found" in msg:
            return ProviderError(ProviderErrorCode.INVALID_REQUEST, str(exc), 404, provider="azure")

        status = getattr(exc, "status_code", 0) or getattr(exc, "http_status", 0)
        if status in (400, 404):
            return ProviderError(ProviderErrorCode.INVALID_REQUEST, str(exc), status, provider="azure")
        if status in (500, 502, 503):
            return ProviderError(ProviderErrorCode.SERVER_ERROR, str(exc), status, provider="azure")

        return ProviderError(ProviderErrorCode.API_ERROR, str(exc), status, provider="azure")

    async def cleanup(self) -> None:
        if self._aclient:
            await self._aclient.close()
            self._aclient = None

    def to_dict(self) -> dict[str, Any]:
        base = super().to_dict()
        base["endpoint_set"] = bool(self._endpoint)
        base["api_key_set"] = bool(self._api_key)
        base["api_version"] = self._api_version
        base["deployment"] = self._model
        return base
