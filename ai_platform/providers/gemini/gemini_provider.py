from __future__ import annotations
import os
import time
from typing import Any, AsyncIterator, Optional
from datetime import datetime, timezone

from ..base_provider import (
    BaseProvider, ModelInfo, ChatResponse, Choice, Usage,
    StreamChunk, HealthStatus, ProviderLimits, PricingInfo,
)


class GeminiProvider(BaseProvider):
    def __init__(self, config: Any):
        super().__init__(config)
        self._model = None

    def _get_api_key(self) -> str:
        return self.config.api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""

    def _get_model(self, model_name: str = ""):
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError("google-generativeai library required. pip install google-generativeai")
        api_key = self._get_api_key()
        genai.configure(api_key=api_key)
        model = model_name or self.config.default_model or "gemini-1.5-pro"
        return genai.GenerativeModel(model)

    async def authenticate(self) -> str:
        try:
            import google.generativeai as genai
            genai.configure(api_key=self._get_api_key())
            genai.list_models()
            return "authenticated"
        except Exception as e:
            raise RuntimeError(f"Gemini authentication failed: {e}")

    async def list_models(self) -> list[ModelInfo]:
        return [
            ModelInfo(id="gemini-1.5-pro", name="Gemini 1.5 Pro", provider="gemini", capabilities=["chat", "vision"], context_window=1000000, max_tokens=8192),
            ModelInfo(id="gemini-1.5-flash", name="Gemini 1.5 Flash", provider="gemini", capabilities=["chat", "vision"], context_window=1000000, max_tokens=8192),
            ModelInfo(id="gemini-1.0-pro", name="Gemini 1.0 Pro", provider="gemini", capabilities=["chat"], context_window=32768, max_tokens=2048),
        ]

    async def chat(self, messages: list[dict], config: dict[str, Any]) -> ChatResponse:
        model_name = config.get("model") or self.config.default_model or "gemini-1.5-pro"
        try:
            import google.generativeai as genai
            genai.configure(api_key=self._get_api_key())
            model = genai.GenerativeModel(model_name)
            prompt = self._convert_messages_to_prompt(messages)
            resp = model.generate_content(prompt)
            usage = Usage(
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
            )
            if hasattr(resp, 'usage_metadata') and resp.usage_metadata:
                usage.prompt_tokens = getattr(resp.usage_metadata, 'prompt_token_count', 0) or 0
                usage.completion_tokens = getattr(resp.usage_metadata, 'candidates_token_count', 0) or 0
                usage.total_tokens = usage.prompt_tokens + usage.completion_tokens
            return ChatResponse(
                id=str(getattr(resp, 'result_id', '')),
                model=model_name,
                choices=[Choice(index=0, message={"role": "assistant", "content": resp.text if hasattr(resp, 'text') else str(resp)}, finish_reason="stop")],
                usage=usage,
                provider="gemini",
            )
        except Exception as e:
            return ChatResponse(
                id="fallback",
                model=model_name,
                choices=[Choice(index=0, message={"role": "assistant", "content": f"[Gemini error: {e}]"})],
                provider="gemini",
            )

    def _convert_messages_to_prompt(self, messages: list[dict]) -> str:
        parts = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            prefix = "" if role == "assistant" else f"{role}: "
            parts.append(f"{prefix}{content}")
        return "\n".join(parts)

    async def stream(self, messages: list[dict], config: dict[str, Any]) -> AsyncIterator[StreamChunk]:
        model_name = config.get("model") or self.config.default_model or "gemini-1.5-pro"
        try:
            import google.generativeai as genai
            genai.configure(api_key=self._get_api_key())
            model = genai.GenerativeModel(model_name)
            prompt = self._convert_messages_to_prompt(messages)
            resp = model.generate_content(prompt, stream=True)
            for chunk in resp:
                if hasattr(chunk, 'text') and chunk.text:
                    yield StreamChunk(delta=chunk.text, model=model_name)
            yield StreamChunk(delta="", finish_reason="stop", model=model_name)
        except Exception as e:
            yield StreamChunk(delta=f"[Stream error: {e}]", finish_reason="error")

    async def embeddings(self, texts: list[str]) -> list[list[float]]:
        try:
            import google.generativeai as genai
            genai.configure(api_key=self._get_api_key())
            result = []
            for text in texts:
                emb = genai.embed_content(model="models/text-embedding-004", content=text)
                result.append(emb['embedding'])
            return result
        except Exception:
            return [[0.0] * 768 for _ in texts]

    async def health(self) -> HealthStatus:
        start = time.monotonic()
        try:
            import google.generativeai as genai
            genai.configure(api_key=self._get_api_key())
            list(genai.list_models())  # ensure iteration
            elapsed = (time.monotonic() - start) * 1000
            return HealthStatus(status="healthy", latency_ms=elapsed, last_check=datetime.now(timezone.utc))
        except Exception as e:
            elapsed = (time.monotonic() - start) * 1000
            return HealthStatus(status="unhealthy", latency_ms=elapsed, last_check=datetime.now(timezone.utc), error=str(e))

    async def limits(self) -> ProviderLimits:
        return ProviderLimits(max_requests_per_minute=60, max_tokens_per_minute=120000, max_concurrent_requests=10)

    async def pricing(self) -> PricingInfo:
        return PricingInfo(input_per_1k=0.000125, output_per_1k=0.000375, currency="USD")
