from __future__ import annotations

import asyncio
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
# Pricing (per 1K tokens, USD) — approximate, varies by model
# ---------------------------------------------------------------------------

HF_PRICING: dict[str, PricingRow] = {
    "HuggingFaceH4/zephyr-7b-beta": PricingRow(0.0, 0.0),  # Free Inference API (rate-limited)
    "meta-llama/Llama-3.3-70B-Instruct": PricingRow(0.0035, 0.005),
    "meta-llama/Llama-3.1-8B-Instruct": PricingRow(0.0005, 0.0008),
    "mistralai/Mistral-7B-Instruct-v0.3": PricingRow(0.0002, 0.0002),
    "mistralai/Mixtral-8x7B-Instruct-v0.1": PricingRow(0.002, 0.002),
    "google/gemma-2-27b-it": PricingRow(0.001, 0.001),
    "google/gemma-2-9b-it": PricingRow(0.0003, 0.0003),
    "Qwen/Qwen2.5-72B-Instruct": PricingRow(0.0035, 0.005),
    "Qwen/Qwen2.5-7B-Instruct": PricingRow(0.0003, 0.0005),
    "microsoft/Phi-3-mini-4k-instruct": PricingRow(0.0001, 0.0001),
}


class HuggingFaceProvider(BaseLLMProvider):
    """HuggingFace provider using huggingface_hub AsyncInferenceClient.

    Supports:
    - Chat completions via Inference API (hosted or dedicated endpoint)
    - Streaming
    - Tool calling
    - OpenAI-compatible message format
    - Hundreds of open models (Llama, Mistral, Qwen, Gemma, Phi, etc.)
    - Automatic retry and rate limiting
    """

    def __init__(
        self,
        model: str = "HuggingFaceH4/zephyr-7b-beta",
        api_token: str = "",
        base_url: str | None = None,
        max_retries: int = 3,
        requests_per_minute: int = 30,
    ) -> None:
        super().__init__(name="huggingface", model=model)
        self._api_token = api_token or os.getenv("HUGGINGFACE_API_KEY") or os.getenv("HF_API_KEY", "")
        self._base_url = base_url or os.getenv("HF_INFERENCE_ENDPOINT")
        self._max_retries = max_retries
        self._pricing = HF_PRICING
        self._client: Any = None
        if self._api_token:
            self.set_rate_limit(requests_per_minute)

    # ── Client ──────────────────────────────────────────────────────

    def _get_client(self):
        if self._client is None:
            try:
                from huggingface_hub import AsyncInferenceClient

                kwargs: dict[str, Any] = {
                    "token": self._api_token or None,
                }
                if self._base_url:
                    kwargs["base_url"] = self._base_url

                self._client = AsyncInferenceClient(**kwargs)
            except ImportError:
                raise ProviderError(
                    ProviderErrorCode.API_ERROR,
                    "huggingface_hub library required. pip install huggingface_hub",
                    provider="huggingface",
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

        try:
            resp = await client.chat_completion(
                messages=messages,
                model=model,
                stream=False,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 4096),
                top_p=kwargs.get("top_p", 1.0),
                frequency_penalty=kwargs.get("frequency_penalty"),
                presence_penalty=kwargs.get("presence_penalty"),
                stop=kwargs.get("stop_sequences") or kwargs.get("stop"),
                seed=kwargs.get("seed"),
                tools=tools,
                tool_choice=kwargs.get("tool_choice", "auto"),
                response_format=response_format,
            )
        except Exception as e:
            raise self._classify_error(e)

        return self._parse_response(resp, prompt)

    async def _consume_stream(self, prompt: str, **kwargs: Any) -> AsyncIterator[dict[str, Any]]:
        client = self._get_client()
        messages = self._build_messages(prompt, kwargs)
        model = kwargs.get("model") or self._model
        tools = kwargs.get("tools")
        response_format = kwargs.get("response_format")

        try:
            stream = await client.chat_completion(
                messages=messages,
                model=model,
                stream=True,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 4096),
                top_p=kwargs.get("top_p", 1.0),
                frequency_penalty=kwargs.get("frequency_penalty"),
                presence_penalty=kwargs.get("presence_penalty"),
                stop=kwargs.get("stop_sequences") or kwargs.get("stop"),
                seed=kwargs.get("seed"),
                tools=tools,
                tool_choice=kwargs.get("tool_choice", "auto"),
                response_format=response_format,
            )
        except Exception as e:
            raise self._classify_error(e)

        usage_info: dict[str, int] = {}
        async for chunk in stream:
            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta
            finish = chunk.choices[0].finish_reason
            # Tools from stream
            tool_calls_delta = None

            content = ""
            if hasattr(delta, "content") and delta.content:
                content = delta.content

            # Handle tool calls in stream
            if hasattr(delta, "tool_calls") and delta.tool_calls:
                tool_calls_delta = []
                for tc in delta.tool_calls:
                    fn = tc.function
                    tool_calls_delta.append({
                        "id": tc.id or "",
                        "type": "function",
                        "function": {
                            "name": fn.name if fn else "",
                            "arguments": fn.arguments if fn else "",
                        },
                    })

            if chunk.usage:
                usage_info = {
                    "prompt_tokens": chunk.usage.prompt_tokens or 0,
                    "completion_tokens": chunk.usage.completion_tokens or 0,
                    "total_tokens": chunk.usage.total_tokens or 0,
                }
                self._track_usage(usage_info["prompt_tokens"], usage_info["completion_tokens"])

            yield {
                "content": content,
                "finish_reason": finish,
                "delta": StreamDelta(content=content, finish_reason=finish, tool_calls=tool_calls_delta),
                "usage": usage_info or None,
            }

        if usage_info:
            self._track_usage(usage_info.get("prompt_tokens", 0), usage_info.get("completion_tokens", 0))

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

    def _parse_response(self, resp: Any, prompt: str) -> dict[str, Any]:
        choice = resp.choices[0] if resp.choices else None
        if not choice:
            return {"content": "", "success": True, "finish_reason": "stop", **self._track_usage(0, 0)}

        message = choice.message
        content = message.content or ""
        tool_calls = None
        if hasattr(message, "tool_calls") and message.tool_calls:
            tool_calls = []
            for tc in message.tool_calls:
                fn = tc.function
                tool_calls.append({
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": fn.name if fn else "",
                        "arguments": fn.arguments if fn else "",
                    },
                })

        pt = resp.usage.prompt_tokens if resp.usage else count_tokens(prompt)
        ct = resp.usage.completion_tokens if resp.usage else count_tokens(content)

        result: dict[str, Any] = {
            "content": content,
            "success": True,
            "finish_reason": choice.finish_reason or "stop",
            **self._track_usage(pt, ct),
        }
        if tool_calls:
            result["tool_calls"] = tool_calls
        return result

    # ── Error classification ────────────────────────────────────────

    def _classify_error(self, exc: Exception) -> ProviderError:
        msg = str(exc).lower()

        if "401" in msg or "unauthorized" in msg or "token" in msg:
            return ProviderError(ProviderErrorCode.AUTH, str(exc), 401, provider="huggingface")
        if "429" in msg or "rate limit" in msg or "too many requests" in msg:
            return ProviderError(ProviderErrorCode.RATE_LIMIT, str(exc), 429, provider="huggingface")
        if "timeout" in msg or "timed out" in msg:
            return ProviderError(ProviderErrorCode.TIMEOUT, str(exc), 408, provider="huggingface")
        if "400" in msg:
            return ProviderError(ProviderErrorCode.INVALID_REQUEST, str(exc), 400, provider="huggingface")
        if "500" in msg or "502" in msg or "503" in msg:
            return ProviderError(ProviderErrorCode.SERVER_ERROR, str(exc), 500, provider="huggingface")

        return ProviderError(ProviderErrorCode.API_ERROR, str(exc), 0, provider="huggingface")

    # ── Health ───────────────────────────────────────────────────────

    async def health(self) -> dict[str, Any]:
        import time as time_module

        start = time_module.monotonic()
        try:
            client = self._get_client()
            # Try a minimal chat completion as health check
            await client.chat_completion(
                messages=[{"role": "user", "content": "test"}],
                model=self._model,
                max_tokens=1,
            )
            elapsed = (time_module.monotonic() - start) * 1000
            return {"status": "healthy", "latency_ms": round(elapsed, 1), "provider": "huggingface", "model": self._model}
        except Exception as e:
            elapsed = (time_module.monotonic() - start) * 1000
            return {"status": "unhealthy", "latency_ms": round(elapsed, 1), "error": str(e), "provider": "huggingface"}

    # ── Models ───────────────────────────────────────────────────────

    async def list_models(self) -> list[dict[str, Any]]:
        return [
            {"id": "meta-llama/Llama-3.3-70B-Instruct", "name": "Llama 3.3 70B", "provider": "Meta", "capabilities": ["chat", "tools"], "context_window": 128000},
            {"id": "meta-llama/Llama-3.1-8B-Instruct", "name": "Llama 3.1 8B", "provider": "Meta", "capabilities": ["chat", "tools"], "context_window": 128000},
            {"id": "mistralai/Mistral-7B-Instruct-v0.3", "name": "Mistral 7B", "provider": "Mistral", "capabilities": ["chat"], "context_window": 32768},
            {"id": "mistralai/Mixtral-8x7B-Instruct-v0.1", "name": "Mixtral 8x7B", "provider": "Mistral", "capabilities": ["chat"], "context_window": 32768},
            {"id": "google/gemma-2-27b-it", "name": "Gemma 2 27B", "provider": "Google", "capabilities": ["chat"], "context_window": 8192},
            {"id": "Qwen/Qwen2.5-72B-Instruct", "name": "Qwen 2.5 72B", "provider": "Alibaba", "capabilities": ["chat", "tools"], "context_window": 32768},
            {"id": "microsoft/Phi-3-mini-4k-instruct", "name": "Phi-3 Mini", "provider": "Microsoft", "capabilities": ["chat"], "context_window": 4096},
            {"id": "HuggingFaceH4/zephyr-7b-beta", "name": "Zephyr 7B", "provider": "HuggingFace H4", "capabilities": ["chat"], "context_window": 8192},
        ]

    async def cleanup(self) -> None:
        self._client = None

    def to_dict(self) -> dict[str, Any]:
        base = super().to_dict()
        base["api_token_set"] = bool(self._api_token)
        base["base_url"] = self._base_url
        return base
