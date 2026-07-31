from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncIterator
from typing import Any

from .base_provider import (
    GEMINI_PRICING,
    BaseLLMProvider,
    ProviderError,
    ProviderErrorCode,
    StreamDelta,
    _exponential_backoff,
    _is_retryable,
    count_tokens,
)


class GoogleProvider(BaseLLMProvider):
    """Google Gemini provider using the google-generativeai SDK.

    Supports:
    - Chat (gemini-2.0-flash, gemini-2.0-flash-lite, gemini-1.5-pro, gemini-1.5-flash)
    - Streaming
    - Vision (inline image data and file uploads)
    - Function calling (tools via FunctionDeclaration)
    - Safety settings
    - System instructions
    - JSON mode (response_mime_type="application/json")
    - Automatic retry with exponential backoff
    - Rate limiting
    """

    SAFETY_SETTINGS = None  # Use defaults

    def __init__(
        self,
        model: str = "gemini-2.0-flash",
        api_key: str = "",
        max_retries: int = 3,
        requests_per_minute: int = 60,
    ) -> None:
        super().__init__(name="google", model=model)
        self._api_key = api_key or os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
        self._max_retries = max_retries
        self._pricing = GEMINI_PRICING
        self._model_instance: Any = None
        if self._api_key:
            self.set_rate_limit(requests_per_minute)

    # ── Client ──────────────────────────────────────────────────────

    def _get_model(self):
        if self._model_instance is None:
            try:
                import google.generativeai as genai

                genai.configure(api_key=self._api_key)
                self._genai = genai
                self._model_instance = genai.GenerativeModel(
                    model_name=self._model,
                    system_instruction=None,
                    safety_settings=self.SAFETY_SETTINGS,
                )
            except ImportError:
                raise ProviderError(
                    ProviderErrorCode.API_ERROR,
                    "google-generativeai library required. pip install google-generativeai",
                    provider="google",
                )
            except Exception as e:
                raise self._classify_error(e)
        return self._model_instance

    def _build_generation_config(self, kwargs: dict[str, Any]) -> Any:
        """Build generation config dict compatible with genai.GenerationConfig."""
        config = {
            "temperature": kwargs.get("temperature", 0.7),
            "max_output_tokens": kwargs.get("max_tokens", 8192),
            "top_p": kwargs.get("top_p", 1.0),
            "top_k": kwargs.get("top_k", 40),
        }

        response_mime_type = kwargs.get("response_mime_type")
        if response_mime_type:
            config["response_mime_type"] = response_mime_type

        response_schema = kwargs.get("response_schema")
        if response_schema:
            config["response_schema"] = response_schema

        return config

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
        model = self._get_model()
        config = self._build_generation_config(kwargs)
        contents = self._build_contents(prompt, kwargs)
        tools = self._build_tools(kwargs)
        system_instruction = kwargs.get("system")

        try:
            # Google's SDK is primarily synchronous; run in executor for async
            import functools

            fn = functools.partial(
                model.generate_content,
                contents=contents,
                generation_config=config,
                safety_settings=self.SAFETY_SETTINGS,
                tools=tools or None,
                system_instruction=system_instruction,
            )
            loop = asyncio.get_running_loop()
            resp = await loop.run_in_executor(None, fn)
        except Exception as e:
            raise self._classify_error(e)

        content_text = resp.text if hasattr(resp, "text") else ""
        finish_reason = "stop"
        if resp.candidates and resp.candidates[0].finish_reason:
            fr = resp.candidates[0].finish_reason
            finish_reason = fr.name if hasattr(fr, "name") else str(fr)

        # Extract function calls
        tool_calls = []
        if resp.candidates and resp.candidates[0].content.parts:
            for part in resp.candidates[0].content.parts:
                if hasattr(part, "function_call") and part.function_call:
                    fc = part.function_call
                    import json

                    tool_calls.append(
                        {
                            "id": fc.name,
                            "type": "function",
                            "function": {
                                "name": fc.name,
                                "arguments": json.dumps(
                                    dict(fc.args.items()) if hasattr(fc.args, "items") else fc.args
                                ),
                            },
                        }
                    )

        # Track usage
        pt = count_tokens(prompt)
        ct = count_tokens(content_text)
        if hasattr(resp, "usage_metadata") and resp.usage_metadata:
            pt = resp.usage_metadata.prompt_token_count or pt
            ct = resp.usage_metadata.candidates_token_count or ct

        result = {
            "content": content_text,
            "success": True,
            "finish_reason": finish_reason,
            **self._track_usage(pt, ct),
        }
        if tool_calls:
            result["tool_calls"] = tool_calls
        return result

    async def _stream_chunks(self, prompt: str, **kwargs: Any) -> AsyncIterator[dict[str, Any]]:
        """Stream chunks from Gemini."""
        model = self._get_model()
        config = self._build_generation_config(kwargs)
        contents = self._build_contents(prompt, kwargs)
        tools = self._build_tools(kwargs)
        system_instruction = kwargs.get("system")

        try:
            import functools

            fn = functools.partial(
                model.generate_content,
                contents=contents,
                generation_config=config,
                safety_settings=self.SAFETY_SETTINGS,
                stream=True,
                tools=tools or None,
                system_instruction=system_instruction,
            )
            loop = asyncio.get_running_loop()

            # Gemini streaming is sync - run in executor
            stream = await loop.run_in_executor(None, fn)

            # Iterate the sync stream in executor
            for chunk in stream:
                text = chunk.text if hasattr(chunk, "text") else ""
                yield {
                    "content": text,
                    "finish_reason": None,
                    "delta": StreamDelta(content=text),
                    "usage": None,
                }

                # Check finish on last chunk
                if hasattr(chunk, "candidates") and chunk.candidates:
                    fr = chunk.candidates[0].finish_reason
                    if fr and fr.name != "FINISH_REASON_UNSPECIFIED" and fr.name != "STOP":
                        yield {
                            "content": "",
                            "finish_reason": fr.name.lower() if hasattr(fr, "name") else "stop",
                            "delta": StreamDelta(finish_reason=fr.name.lower() if hasattr(fr, "name") else "stop"),
                            "usage": None,
                        }

            # Final chunk
            yield {
                "content": "",
                "finish_reason": "stop",
                "delta": StreamDelta(finish_reason="stop"),
                "usage": None,
            }

        except Exception as e:
            raise self._classify_error(e)

    # ── Health ──────────────────────────────────────────────────────

    async def health(self) -> dict[str, Any]:
        import time as time_module

        start = time_module.monotonic()
        try:
            self._get_model()
            # Simple test - list models via SDK
            import functools

            fn = functools.partial(self._genai.list_models)
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, fn)
            elapsed = (time_module.monotonic() - start) * 1000
            return {"status": "healthy", "latency_ms": round(elapsed, 1), "provider": "google", "model": self._model}
        except Exception as e:
            elapsed = (time_module.monotonic() - start) * 1000
            return {"status": "unhealthy", "latency_ms": round(elapsed, 1), "error": str(e), "provider": "google"}

    # ─── Model listing ────────────────────────────────────────────

    async def list_models(self) -> list[dict[str, Any]]:
        return [
            {
                "id": "gemini-2.0-flash",
                "name": "Gemini 2.0 Flash",
                "provider": "google",
                "capabilities": ["chat", "vision", "tools", "json"],
                "context_window": 1000000,
                "max_tokens": 8192,
            },
            {
                "id": "gemini-2.0-flash-lite",
                "name": "Gemini 2.0 Flash Lite",
                "provider": "google",
                "capabilities": ["chat", "vision", "tools"],
                "context_window": 1000000,
                "max_tokens": 8192,
            },
            {
                "id": "gemini-1.5-pro",
                "name": "Gemini 1.5 Pro",
                "provider": "google",
                "capabilities": ["chat", "vision", "tools", "json"],
                "context_window": 2000000,
                "max_tokens": 8192,
            },
            {
                "id": "gemini-1.5-flash",
                "name": "Gemini 1.5 Flash",
                "provider": "google",
                "capabilities": ["chat", "vision", "tools"],
                "context_window": 1000000,
                "max_tokens": 8192,
            },
            {
                "id": "gemini-pro",
                "name": "Gemini Pro",
                "provider": "google",
                "capabilities": ["chat", "tools"],
                "context_window": 32768,
                "max_tokens": 4096,
            },
            {
                "id": "gemini-pro-vision",
                "name": "Gemini Pro Vision",
                "provider": "google",
                "capabilities": ["chat", "vision"],
                "context_window": 32768,
                "max_tokens": 4096,
            },
        ]

    # ── Vision helper ───────────────────────────────────────────────

    def build_vision_contents(self, text: str, image_data: str, mime_type: str = "image/png") -> list[Any]:
        """Build contents with image for vision requests."""
        import google.generativeai as genai

        return [
            text,
            genai.upload_file_from_bytes(image_data, mime_type=mime_type)
            if not image_data.startswith("http")
            else genai.upload_file(image_data),
        ]

    # ── Helpers ─────────────────────────────────────────────────────

    def _build_contents(self, prompt: str, kwargs: dict[str, Any]) -> str | list[str]:
        """Build content parts including chat history if provided."""
        chat_history = kwargs.get("messages", [])
        if chat_history:
            parts = []
            for msg in chat_history:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                parts.append(f"{role}: {content}")
            parts.append(f"user: {prompt}")
            return "\n".join(parts)
        return prompt

    def _build_tools(self, kwargs: dict[str, Any]) -> list[Any] | None:
        """Convert tool definitions to Gemini format."""
        tools = kwargs.get("tools")
        if not tools:
            return None

        from google.generativeai.types import FunctionDeclaration, Tool

        declarations = []
        for tool in tools:
            if isinstance(tool, dict):
                fn_name = tool.get("function", {}).get("name", "")
                fn_desc = tool.get("function", {}).get("description", "")
                fn_params = tool.get("function", {}).get("parameters", {})
                declarations.append(
                    FunctionDeclaration(
                        name=fn_name,
                        description=fn_desc,
                        parameters=fn_params,
                    )
                )
        return [Tool(function_declarations=declarations)] if declarations else None

    def _classify_error(self, exc: Exception) -> ProviderError:
        msg = str(exc).lower()

        if "api key" in msg or "unauthorized" in msg or "permission" in msg or "auth" in msg:
            return ProviderError(ProviderErrorCode.AUTH, str(exc), 401, provider="google")
        if "429" in msg or "rate limit" in msg or "quota" in msg or "resource exhausted" in msg:
            return ProviderError(ProviderErrorCode.RATE_LIMIT, str(exc), 429, provider="google")
        if "timeout" in msg or "deadline exceeded" in msg:
            return ProviderError(ProviderErrorCode.TIMEOUT, str(exc), 408, provider="google")
        if "context" in msg or "length" in msg or "too long" in msg:
            return ProviderError(ProviderErrorCode.CONTEXT_LENGTH, str(exc), 400, provider="google")
        if "safety" in msg or "blocked" in msg or "finish_reason" in msg:
            return ProviderError(ProviderErrorCode.CONTENT_FILTER, str(exc), 400, provider="google")
        if "500" in msg or "502" in msg or "503" in msg or "unavailable" in msg:
            return ProviderError(ProviderErrorCode.SERVER_ERROR, str(exc), 503, provider="google")
        if "invalid" in msg or "bad request" in msg:
            return ProviderError(ProviderErrorCode.INVALID_REQUEST, str(exc), 400, provider="google")

        return ProviderError(ProviderErrorCode.API_ERROR, str(exc), 0, provider="google")

    def to_dict(self) -> dict[str, Any]:
        base = super().to_dict()
        base["api_key_set"] = bool(self._api_key)
        return base
