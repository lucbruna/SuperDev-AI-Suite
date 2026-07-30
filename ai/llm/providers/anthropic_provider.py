from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncIterator
from typing import Any

from .base_provider import (
    ANTHROPIC_PRICING,
    BaseLLMProvider,
    ProviderError,
    ProviderErrorCode,
    StreamDelta,
    _exponential_backoff,
    _is_retryable,
    count_tokens,
)


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude provider using the official anthropic SDK.

    Supports:
    - Chat (claude-3-5-sonnet, claude-3-opus, claude-3-haiku, claude-2.1)
    - Streaming via text_stream
    - Vision (image content blocks)
    - Tool/function calling (tool_use blocks)
    - Extended thinking (claude-3-7-sonnet)
    - Automatic retry with exponential backoff
    - Rate limiting
    """

    def __init__(
        self,
        model: str = "claude-3-5-sonnet-20241022",
        api_key: str = "",
        base_url: str | None = None,
        max_retries: int = 3,
        requests_per_minute: int = 50,
    ) -> None:
        super().__init__(name="anthropic", model=model)
        self._api_key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
        self._base_url = base_url or os.getenv("ANTHROPIC_BASE_URL")
        self._max_retries = max_retries
        self._pricing = ANTHROPIC_PRICING
        self._client: Any = None
        if self._api_key:
            self.set_rate_limit(requests_per_minute)

    # ── Client ──────────────────────────────────────────────────────

    def _get_client(self):
        if self._client is None:
            try:
                from anthropic import AsyncAnthropic
                kwargs: dict[str, Any] = {"api_key": self._api_key, "max_retries": 0}
                if self._base_url:
                    kwargs["base_url"] = self._base_url
                self._client = AsyncAnthropic(**kwargs)
            except ImportError:
                raise ProviderError(ProviderErrorCode.API_ERROR, "anthropic library required. pip install anthropic", provider="anthropic")
        return self._client

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
        system, messages = self._build_messages(prompt, kwargs)
        model = kwargs.get("model") or self._model
        tools = kwargs.get("tools")
        max_tokens = kwargs.get("max_tokens", 4096)

        body: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": kwargs.get("temperature", 0.7),
        }
        if system:
            body["system"] = system
        if tools:
            body["tools"] = tools

        try:
            resp = await client.messages.create(**body)
        except Exception as e:
            raise self._classify_error(e)

        # Extract text content and tool calls from content blocks
        content_text = ""
        tool_calls = []
        for block in resp.content:
            if block.type == "text":
                content_text += block.text
            elif block.type == "tool_use":
                tool_calls.append({
                    "id": block.id,
                    "type": "function",
                    "function": {"name": block.name, "arguments": str(block.input)},
                })

        pt = resp.usage.input_tokens if resp.usage else count_tokens(prompt)
        ct = resp.usage.output_tokens if resp.usage else count_tokens(content_text)

        result = {
            "content": content_text,
            "success": True,
            "finish_reason": resp.stop_reason or "stop",
            **self._track_usage(pt, ct),
        }
        if tool_calls:
            result["tool_calls"] = tool_calls
        return result

    async def _stream_chunks(self, prompt: str, **kwargs: Any) -> AsyncIterator[dict[str, Any]]:
        """Stream chunks from Anthropic using text_stream."""
        client = self._get_client()
        system, messages = self._build_messages(prompt, kwargs)
        model = kwargs.get("model") or self._model
        tools = kwargs.get("tools")
        max_tokens = kwargs.get("max_tokens", 4096)

        body: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": kwargs.get("temperature", 0.7),
        }
        if system:
            body["system"] = system
        if tools:
            body["tools"] = tools

        try:
            async with client.messages.stream(**body) as stream:
                async for text in stream.text_stream:
                    yield {
                        "content": text,
                        "finish_reason": None,
                        "delta": StreamDelta(content=text),
                        "usage": None,
                    }

                final = await stream.get_final_message()
                usage_info = {}
                if final.usage:
                    usage_info = {
                        "prompt_tokens": final.usage.input_tokens or 0,
                        "completion_tokens": final.usage.output_tokens or 0,
                        "total_tokens": (final.usage.input_tokens or 0) + (final.usage.output_tokens or 0),
                    }

                yield {
                    "content": "",
                    "finish_reason": "stop",
                    "delta": StreamDelta(finish_reason="stop", usage=usage_info),
                    "usage": usage_info or None,
                }

                if usage_info:
                    self._track_usage(usage_info.get("prompt_tokens", 0), usage_info.get("completion_tokens", 0))
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
            return {"status": "healthy", "latency_ms": round(elapsed, 1), "provider": "anthropic", "model": self._model}
        except Exception as e:
            elapsed = (time_module.monotonic() - start) * 1000
            return {"status": "unhealthy", "latency_ms": round(elapsed, 1), "error": str(e), "provider": "anthropic"}

    # ─── Model listing ────────────────────────────────────────────

    async def list_models(self) -> list[dict[str, Any]]:
        return [
            {"id": "claude-3-5-sonnet-20241022", "name": "Claude 3.5 Sonnet", "provider": "anthropic", "capabilities": ["chat", "vision", "tools"], "context_window": 200000, "max_tokens": 8192},
            {"id": "claude-3-5-haiku-20241022", "name": "Claude 3.5 Haiku", "provider": "anthropic", "capabilities": ["chat", "vision", "tools"], "context_window": 200000, "max_tokens": 8192},
            {"id": "claude-3-opus-20240229", "name": "Claude 3 Opus", "provider": "anthropic", "capabilities": ["chat", "vision", "tools"], "context_window": 200000, "max_tokens": 4096},
            {"id": "claude-3-haiku-20240307", "name": "Claude 3 Haiku", "provider": "anthropic", "capabilities": ["chat", "vision", "tools"], "context_window": 200000, "max_tokens": 4096},
            {"id": "claude-2.1", "name": "Claude 2.1", "provider": "anthropic", "capabilities": ["chat"], "context_window": 100000, "max_tokens": 4096},
            {"id": "claude-3-7-sonnet-20250219", "name": "Claude 3.7 Sonnet", "provider": "anthropic", "capabilities": ["chat", "vision", "tools", "thinking"], "context_window": 200000, "max_tokens": 64000},
        ]

    # ── Vision helper ───────────────────────────────────────────────

    def build_vision_messages(self, text: str, image_url: str, media_type: str = "image/png") -> list[dict[str, Any]]:
        """Build messages with image content for vision requests."""
        image_data = self._resolve_image_data(image_url)
        return [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": text},
                    {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": image_data}},
                ],
            }
        ]

    def _resolve_image_data(self, image_url: str) -> str:
        """Resolve image URL to base64 data. Supports data URIs and URLs."""
        if image_url.startswith("data:image"):
            return image_url.split(",")[-1]
        if image_url.startswith("http"):
            import base64
            import httpx
            resp = httpx.get(image_url)
            resp.raise_for_status()
            return base64.b64encode(resp.content).decode()
        return image_url

    # ── Helpers ─────────────────────────────────────────────────────

    def _build_messages(self, prompt: str, kwargs: dict[str, Any]) -> tuple[str | None, list[dict[str, Any]]]:
        """Build messages for Anthropic format. Returns (system_prompt, messages)."""
        system = kwargs.get("system")

        messages: list[dict[str, Any]] = []
        chat_history = kwargs.get("messages", [])
        if chat_history:
            # Anthropic expects user/assistant alternation, starting with user
            for msg in chat_history:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "system":
                    system = (system or "") + "\n" + content if isinstance(content, str) else content
                    continue
                messages.append({"role": role, "content": content})

        messages.append({"role": "user", "content": prompt})
        return system, messages

    def _classify_error(self, exc: Exception) -> ProviderError:
        msg = str(exc).lower()

        if "401" in msg or "unauthorized" in msg or "api key" in msg:
            return ProviderError(ProviderErrorCode.AUTH, str(exc), 401, provider="anthropic")
        if "429" in msg or "rate limit" in msg:
            return ProviderError(ProviderErrorCode.RATE_LIMIT, str(exc), 429, provider="anthropic")
        if "timeout" in msg or "timed out" in msg:
            return ProviderError(ProviderErrorCode.TIMEOUT, str(exc), 408, provider="anthropic")
        if "context" in msg and ("length" in msg or "exceed" in msg):
            return ProviderError(ProviderErrorCode.CONTEXT_LENGTH, str(exc), 400, provider="anthropic")
        if "content_filter" in msg or "harm" in msg or "safety" in msg:
            return ProviderError(ProviderErrorCode.CONTENT_FILTER, str(exc), 400, provider="anthropic")

        status = getattr(exc, "status_code", 0)
        if status == 400:
            return ProviderError(ProviderErrorCode.INVALID_REQUEST, str(exc), 400, provider="anthropic")
        if status in (500, 502, 503):
            return ProviderError(ProviderErrorCode.SERVER_ERROR, str(exc), status, provider="anthropic")

        return ProviderError(ProviderErrorCode.API_ERROR, str(exc), status, provider="anthropic")

    async def cleanup(self) -> None:
        self._client = None

    def to_dict(self) -> dict[str, Any]:
        base = super().to_dict()
        base["api_key_set"] = bool(self._api_key)
        return base
