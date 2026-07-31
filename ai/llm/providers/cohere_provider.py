from __future__ import annotations

import asyncio
import json
import os
from collections.abc import AsyncIterator
from typing import Any

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

# ---------------------------------------------------------------------------
# Cohere pricing (per 1M tokens → per 1K tokens, USD)
# ---------------------------------------------------------------------------

COHERE_PRICING: dict[str, PricingRow] = {
    "command-r-plus": PricingRow(0.003, 0.015),
    "command-r": PricingRow(0.0015, 0.0075),
    "command-r7b": PricingRow(0.00015, 0.0003),
    "command-light": PricingRow(0.0015, 0.0075),
    "command": PricingRow(0.0015, 0.0075),
    "command-xlarge-beta": PricingRow(0.006, 0.006),
    "command-xlarge-nightly": PricingRow(0.006, 0.006),
}


class CohereProvider(BaseLLMProvider):
    """Cohere provider using the official cohere SDK (v2 API).

    Supports:
    - Chat (Command R+, Command R, Command R7B)
    - Streaming
    - Tool/function calling
    - Automatic retry and rate limiting
    - OpenAI-compatible message format
    """

    def __init__(
        self,
        model: str = "command-r-plus",
        api_key: str = "",
        max_retries: int = 3,
        requests_per_minute: int = 500,
    ) -> None:
        super().__init__(name="cohere", model=model)
        self._api_key = api_key or os.getenv("COHERE_API_KEY", "")
        self._max_retries = max_retries
        self._pricing = COHERE_PRICING
        self._client: Any = None
        if self._api_key:
            self.set_rate_limit(requests_per_minute)

    # ── Client ──────────────────────────────────────────────────────

    def _get_client(self):
        if self._client is None:
            try:
                from cohere import AsyncClientV2

                self._client = AsyncClientV2(api_key=self._api_key)
            except ImportError:
                raise ProviderError(
                    ProviderErrorCode.API_ERROR,
                    "cohere library required. pip install cohere",
                    provider="cohere",
                )
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
                    async for chunk in self._consume_stream(prompt, **kwargs):
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

    # ── Internal generation ─────────────────────────────────────────

    async def _generate(self, prompt: str, **kwargs: Any) -> dict[str, Any]:
        client = self._get_client()
        messages = self._build_messages(prompt, kwargs)
        model = kwargs.get("model") or self._model
        tools = self._convert_tools(kwargs.get("tools"))
        tool_choice = kwargs.get("tool_choice", "AUTO")

        try:
            resp = await client.chat(
                model=model,
                messages=messages,
                tools=tools or None,
                tool_choice=tool_choice,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 4096),
                p=kwargs.get("top_p", 1.0),
                frequency_penalty=kwargs.get("frequency_penalty"),
                presence_penalty=kwargs.get("presence_penalty"),
                stop_sequences=kwargs.get("stop_sequences"),
            )
        except Exception as e:
            raise self._classify_error(e)

        return self._parse_response(resp, prompt)

    async def _consume_stream(self, prompt: str, **kwargs: Any) -> AsyncIterator[dict[str, Any]]:
        client = self._get_client()
        messages = self._build_messages(prompt, kwargs)
        model = kwargs.get("model") or self._model
        tools = self._convert_tools(kwargs.get("tools"))
        tool_choice = kwargs.get("tool_choice", "AUTO")

        try:
            stream = client.chat_stream(
                model=model,
                messages=messages,
                tools=tools or None,
                tool_choice=tool_choice,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 4096),
                p=kwargs.get("top_p", 1.0),
                frequency_penalty=kwargs.get("frequency_penalty"),
                presence_penalty=kwargs.get("presence_penalty"),
                stop_sequences=kwargs.get("stop_sequences"),
            )
        except Exception as e:
            raise self._classify_error(e)

        usage_info: dict[str, int] = {}
        async for event in stream:
            event_type = type(event).__name__

            if event_type == "MessageStartV2ChatStreamResponse":
                # Role signal, no content yet
                pass

            elif event_type == "ContentStartV2ChatStreamResponse":
                pass  # First content delta will follow

            elif event_type == "ContentDeltaV2ChatStreamResponse":
                delta = event.delta
                if delta and delta.message:
                    text = delta.message.content or ""
                    if text:
                        yield {
                            "content": text,
                            "finish_reason": None,
                            "delta": StreamDelta(content=text),
                        }

            elif (
                event_type == "ContentEndV2ChatStreamResponse"
                or event_type == "ToolCallStartV2ChatStreamResponse"
                or event_type == "ToolCallDeltaV2ChatStreamResponse"
            ):
                pass

            elif event_type == "MessageEndV2ChatStreamResponse":
                finish = event.delta and event.delta.finish_reason
                finish_map = {
                    "COMPLETE": "stop",
                    "STOP_SEQUENCE": "stop",
                    "MAX_TOKENS": "length",
                    "TOOL_CALL": "tool_calls",
                    "ERROR": "error",
                    "TIMEOUT": "error",
                }
                finish_reason = finish_map.get(finish, "stop") if finish else "stop"
                yield {
                    "content": "",
                    "finish_reason": finish_reason,
                    "delta": StreamDelta(finish_reason=finish_reason),
                }

            elif event_type == "DebugV2ChatStreamResponse":
                pass

            # Track usage from message end
            if event_type == "MessageEndV2ChatStreamResponse":
                try:
                    usage = event.delta and event.delta.usage
                    if usage and usage.tokens:
                        usage_info = {
                            "prompt_tokens": usage.tokens.input_tokens or 0,
                            "completion_tokens": usage.tokens.output_tokens or 0,
                            "total_tokens": (usage.tokens.input_tokens or 0) + (usage.tokens.output_tokens or 0),
                        }
                        self._track_usage(usage_info["prompt_tokens"], usage_info["completion_tokens"])
                except (AttributeError, TypeError):
                    pass

    # ── Helpers ─────────────────────────────────────────────────────

    def _build_messages(self, prompt: str, kwargs: dict[str, Any]) -> list[dict[str, Any]]:
        """Build messages in OpenAI-compatible format."""
        messages = []

        system = kwargs.get("system")
        if system:
            messages.append({"role": "system", "content": system})

        chat_history = kwargs.get("messages", [])
        if chat_history:
            messages.extend(chat_history)

        messages.append({"role": "user", "content": prompt})
        return messages

    def _convert_tools(self, tools: Any) -> list[dict[str, Any]] | None:
        if not tools:
            return None
        converted = []
        for tool in tools:
            if tool.get("type") == "function":
                fn = tool["function"]
                converted.append(
                    {
                        "type": "function",
                        "function": {
                            "name": fn.get("name", ""),
                            "description": fn.get("description", ""),
                            "parameters": fn.get("parameters", {}),
                        },
                    }
                )
        return converted if converted else None

    def _parse_response(self, resp: Any, prompt: str) -> dict[str, Any]:
        finish_map = {
            "COMPLETE": "stop",
            "STOP_SEQUENCE": "stop",
            "MAX_TOKENS": "length",
            "TOOL_CALL": "tool_calls",
            "ERROR": "error",
            "TIMEOUT": "error",
        }
        finish_reason = finish_map.get(resp.finish_reason, "stop")
        message = resp.message

        # Extract text content from content list
        content = ""
        if message.content:
            parts = [c.text for c in message.content if hasattr(c, "text")]
            content = "".join(parts)

        # Extract tool calls
        tool_calls = None
        if message.tool_calls:
            tool_calls = []
            for tc in message.tool_calls:
                tc_func = tc.function
                tool_calls.append(
                    {
                        "id": tc.id,
                        "type": tc.type or "function",
                        "function": {
                            "name": tc_func.name if tc_func else "",
                            "arguments": json.dumps(tc_func.arguments if tc_func else {}),
                        },
                    }
                )

        # Extract usage
        pt = count_tokens(prompt)
        ct = count_tokens(content)
        if resp.usage and resp.usage.tokens:
            pt = resp.usage.tokens.input_tokens or pt
            ct = resp.usage.tokens.output_tokens or ct

        result: dict[str, Any] = {
            "content": content,
            "success": True,
            "finish_reason": finish_reason,
            **self._track_usage(pt, ct),
        }
        if tool_calls:
            result["tool_calls"] = tool_calls
        return result

    # ── Error classification ────────────────────────────────────────

    def _classify_error(self, exc: Exception) -> ProviderError:
        msg = str(exc).lower()

        if "401" in msg or "unauthorized" in msg or "api key" in msg:
            return ProviderError(ProviderErrorCode.AUTH, str(exc), 401, provider="cohere")
        if "429" in msg or "rate limit" in msg:
            return ProviderError(ProviderErrorCode.RATE_LIMIT, str(exc), 429, provider="cohere")
        if "timeout" in msg or "timed out" in msg:
            return ProviderError(ProviderErrorCode.TIMEOUT, str(exc), 408, provider="cohere")
        if "400" in msg or "invalid" in msg:
            return ProviderError(ProviderErrorCode.INVALID_REQUEST, str(exc), 400, provider="cohere")
        if "500" in msg or "502" in msg or "503" in msg:
            return ProviderError(ProviderErrorCode.SERVER_ERROR, str(exc), 500, provider="cohere")

        return ProviderError(ProviderErrorCode.API_ERROR, str(exc), 0, provider="cohere")

    # ── Health ───────────────────────────────────────────────────────

    async def health(self) -> dict[str, Any]:
        import time as time_module

        start = time_module.monotonic()
        try:
            client = self._get_client()
            result = await client.check_api_key()
            elapsed = (time_module.monotonic() - start) * 1000
            if result and result.valid:
                return {
                    "status": "healthy",
                    "latency_ms": round(elapsed, 1),
                    "provider": "cohere",
                    "model": self._model,
                }
            return {
                "status": "unhealthy",
                "latency_ms": round(elapsed, 1),
                "error": "Invalid API key",
                "provider": "cohere",
            }
        except Exception as e:
            elapsed = (time_module.monotonic() - start) * 1000
            return {"status": "unhealthy", "latency_ms": round(elapsed, 1), "error": str(e), "provider": "cohere"}

    # ── Models ───────────────────────────────────────────────────────

    async def list_models(self) -> list[dict[str, Any]]:
        return [
            {"id": "command-r-plus", "name": "Command R+", "capabilities": ["chat", "tools"], "context_window": 128000},
            {"id": "command-r", "name": "Command R", "capabilities": ["chat", "tools"], "context_window": 128000},
            {"id": "command-r7b", "name": "Command R7B", "capabilities": ["chat", "tools"], "context_window": 128000},
            {"id": "command", "name": "Command", "capabilities": ["chat"], "context_window": 4096},
            {"id": "command-light", "name": "Command Light", "capabilities": ["chat"], "context_window": 4096},
            {"id": "embed-english-v3.0", "name": "Embed English v3", "capabilities": ["embedding"], "dimensions": 1024},
            {
                "id": "embed-multilingual-v3.0",
                "name": "Embed Multilingual v3",
                "capabilities": ["embedding"],
                "dimensions": 1024,
            },
        ]

    async def cleanup(self) -> None:
        if self._client and hasattr(self._client, "close"):
            await self._client.close()
        self._client = None

    def to_dict(self) -> dict[str, Any]:
        base = super().to_dict()
        base["api_key_set"] = bool(self._api_key)
        return base
