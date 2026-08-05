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
# Local model pricing — always free (self-hosted)
# ---------------------------------------------------------------------------

LOCAL_PRICING: dict[str, PricingRow] = {}

# Ollama model → approximate context window
OLLAMA_MODEL_INFO: dict[str, dict[str, Any]] = {
    "llama3.3": {"context_window": 128000, "capabilities": ["chat", "tools"]},
    "llama3.2": {"context_window": 128000, "capabilities": ["chat", "vision", "tools"]},
    "llama3.1": {"context_window": 128000, "capabilities": ["chat", "tools"]},
    "llama3": {"context_window": 8192, "capabilities": ["chat", "tools"]},
    "mistral": {"context_window": 8192, "capabilities": ["chat"]},
    "mixtral": {"context_window": 32768, "capabilities": ["chat"]},
    "codellama": {"context_window": 16384, "capabilities": ["chat"]},
    "gemma2": {"context_window": 8192, "capabilities": ["chat"]},
    "phi3": {"context_window": 4096, "capabilities": ["chat"]},
    "qwen2.5": {"context_window": 32768, "capabilities": ["chat", "tools"]},
    "deepseek-coder": {"context_window": 16384, "capabilities": ["chat"]},
    "nomic-embed-text": {"context_window": 8192, "capabilities": ["embedding"]},
    "mxbai-embed-large": {"context_window": 512, "capabilities": ["embedding"]},
}


class LocalProvider(BaseLLMProvider):
    """Local model provider using Ollama.

    Supports:
    - Chat with any Ollama model (Llama, Mistral, Gemma, Qwen, Phi, etc.)
    - Streaming
    - Tool calling
    - Vision (multimodal models)
    - OpenAI-compatible message format
    - No rate limits (local), full retry control
    """

    def __init__(
        self,
        model: str = "llama3.3",
        endpoint: str = "",
        max_retries: int = 2,
        requests_per_minute: int = 60,
    ) -> None:
        super().__init__(name="local", model=model)
        self._endpoint = endpoint or os.getenv("OLLAMA_BASE_URL") or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self._max_retries = max_retries
        self._pricing = LOCAL_PRICING
        self._client: Any = None
        self.set_rate_limit(requests_per_minute)

    # ── Client ──────────────────────────────────────────────────────

    def _get_client(self):
        if self._client is None:
            try:
                from ollama import AsyncClient

                self._client = AsyncClient(host=self._endpoint)
            except ImportError:
                raise ProviderError(
                    ProviderErrorCode.API_ERROR,
                    "ollama library required. pip install ollama",
                    provider="local",
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
        options = self._build_options(kwargs)

        try:
            resp = await client.chat(
                model=model,
                messages=messages,
                tools=tools or None,
                stream=False,
                options=options or None,
                format=kwargs.get("response_format"),  # JSON mode
            )
        except Exception as e:
            raise self._classify_error(e)

        return self._parse_response(resp, prompt)

    async def _consume_stream(self, prompt: str, **kwargs: Any) -> AsyncIterator[dict[str, Any]]:
        client = self._get_client()
        messages = self._build_messages(prompt, kwargs)
        model = kwargs.get("model") or self._model
        tools = self._convert_tools(kwargs.get("tools"))
        options = self._build_options(kwargs)

        try:
            stream = await client.chat(
                model=model,
                messages=messages,
                tools=tools or None,
                stream=True,
                options=options or None,
                format=kwargs.get("response_format"),
            )
        except Exception as e:
            raise self._classify_error(e)

        usage_info: dict[str, int] = {}
        async for chunk in stream:
            if not chunk.done:
                # Streaming delta
                content = chunk.message.content or ""
                yield {
                    "content": content,
                    "finish_reason": None,
                    "delta": StreamDelta(content=content),
                }
            else:
                # Final chunk with stats
                if chunk.prompt_eval_count is not None and chunk.eval_count is not None:
                    usage_info = {
                        "prompt_tokens": chunk.prompt_eval_count,
                        "completion_tokens": chunk.eval_count,
                        "total_tokens": chunk.prompt_eval_count + chunk.eval_count,
                    }
                    self._track_usage(chunk.prompt_eval_count, chunk.eval_count)

                finish_reason = chunk.done_reason or "stop"
                yield {
                    "content": "",
                    "finish_reason": finish_reason,
                    "delta": StreamDelta(finish_reason=finish_reason),
                    "usage": usage_info or None,
                }

    # ── Helpers ─────────────────────────────────────────────────────

    def _build_messages(self, prompt: str, kwargs: dict[str, Any]) -> list[dict[str, Any]]:
        """Build messages in Ollama-compatible format."""
        messages = []

        system = kwargs.get("system")
        if system:
            messages.append({"role": "system", "content": system})

        chat_history = kwargs.get("messages", [])
        if chat_history:
            messages.extend(chat_history)

        # Check for vision content
        image = kwargs.get("image") or kwargs.get("image_url")
        if image:
            messages.append(
                {
                    "role": "user",
                    "content": prompt,
                    "images": [image],
                }
            )
        else:
            messages.append({"role": "user", "content": prompt})

        return messages

    def _build_options(self, kwargs: dict[str, Any]) -> dict[str, Any] | None:
        """Build Ollama options dict from standard params."""
        options: dict[str, Any] = {}
        if "temperature" in kwargs:
            options["temperature"] = kwargs["temperature"]
        if "top_p" in kwargs:
            options["top_p"] = kwargs["top_p"]
        if "max_tokens" in kwargs:
            options["num_predict"] = kwargs["max_tokens"]
        if "stop_sequences" in kwargs:
            options["stop"] = kwargs["stop_sequences"]
        if "seed" in kwargs:
            options["seed"] = kwargs["seed"]
        if "frequency_penalty" in kwargs:
            options["frequency_penalty"] = kwargs["frequency_penalty"]
        if "presence_penalty" in kwargs:
            options["presence_penalty"] = kwargs["presence_penalty"]
        # passthrough for any Ollama-specific options
        ollama_opts = kwargs.get("ollama_options", {})
        if ollama_opts:
            options.update(ollama_opts)
        return options if options else None

    def _convert_tools(self, tools: Any) -> list[dict[str, Any]] | None:
        if not tools:
            return None
        return tools  # Ollama uses the same OpenAI-compatible tool format

    def _parse_response(self, resp: Any, prompt: str) -> dict[str, Any]:
        message = resp.message
        content = message.content or ""

        # Tool calls
        tool_calls = None
        if message.tool_calls:
            tool_calls = []
            for tc in message.tool_calls:
                # Ollama tool calls have function structure
                tc_dict = tc if isinstance(tc, dict) else tc.model_dump()
                if isinstance(tc_dict, dict):
                    tool_calls.append(
                        {
                            "id": tc_dict.get("id", ""),
                            "type": "function",
                            "function": {
                                "name": tc_dict.get("function", {}).get("name", "")
                                if isinstance(tc_dict.get("function"), dict)
                                else tc_dict.get("function", tc_dict.get("name", "")),
                                "arguments": tc_dict.get("function", {}).get("arguments", "{}")
                                if isinstance(tc_dict.get("function"), dict)
                                else "{}",
                            },
                        }
                    )

        pt = resp.prompt_eval_count if resp.prompt_eval_count is not None else count_tokens(prompt)
        ct = resp.eval_count if resp.eval_count is not None else count_tokens(content)

        result: dict[str, Any] = {
            "content": content,
            "success": True,
            "finish_reason": resp.done_reason or "stop",
            **self._track_usage(pt, ct),
        }
        if tool_calls:
            result["tool_calls"] = tool_calls
        return result

    # ── Error classification ────────────────────────────────────────

    def _classify_error(self, exc: Exception) -> ProviderError:
        msg = str(exc).lower()

        if "connection refused" in msg or "connection error" in msg or "connect" in msg:
            return ProviderError(
                ProviderErrorCode.SERVER_ERROR,
                f"Ollama not running at {self._endpoint}. Start with: ollama serve",
                503,
                provider="local",
            )
        if "not found" in msg or "pull" in msg or "model" in msg:
            return ProviderError(
                ProviderErrorCode.INVALID_REQUEST,
                f"Model not found. Pull with: ollama pull {self._model}",
                404,
                provider="local",
            )
        if "timeout" in msg or "timed out" in msg:
            return ProviderError(ProviderErrorCode.TIMEOUT, str(exc), 408, provider="local")
        if "400" in msg:
            return ProviderError(ProviderErrorCode.INVALID_REQUEST, str(exc), 400, provider="local")

        return ProviderError(ProviderErrorCode.API_ERROR, str(exc), 0, provider="local")

    # ── Health ───────────────────────────────────────────────────────

    async def health(self) -> dict[str, Any]:
        import time as time_module

        start = time_module.monotonic()
        try:
            client = self._get_client()
            # List local models as health check
            models = await client.list()
            model_ids = [m.model for m in models.models] if models.models else []
            model_available = self._model in model_ids or any(self._model in m for m in model_ids)
            elapsed = (time_module.monotonic() - start) * 1000
            return {
                "status": "healthy",
                "latency_ms": round(elapsed, 1),
                "provider": "local",
                "model": self._model,
                "model_available": model_available,
                "ollama_endpoint": self._endpoint,
            }
        except Exception as e:
            elapsed = (time_module.monotonic() - start) * 1000
            return {"status": "unhealthy", "latency_ms": round(elapsed, 1), "error": str(e), "provider": "local"}

    # ── Models ───────────────────────────────────────────────────────

    async def list_models(self) -> list[dict[str, Any]]:
        return [
            {
                "id": model_id,
                "name": model_id,
                "capabilities": info.get("capabilities", ["chat"]),
                "context_window": info.get("context_window", 8192),
            }
            for model_id, info in OLLAMA_MODEL_INFO.items()
        ]

    async def cleanup(self) -> None:
        self._client = None

    def to_dict(self) -> dict[str, Any]:
        base = super().to_dict()
        base["endpoint"] = self._endpoint
        return base
