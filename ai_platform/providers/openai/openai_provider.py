from __future__ import annotations
import os
import time
from typing import Any, AsyncIterator, Optional
from datetime import datetime, timezone

from ..base_provider import (
    BaseProvider, ModelInfo, ChatResponse, Choice, Usage,
    StreamChunk, HealthStatus, ProviderLimits, PricingInfo,
)


class OpenAIProvider(BaseProvider):
    def __init__(self, config: Any):
        super().__init__(config)
        self._client = None
        self._aclient = None

    def _get_api_key(self) -> str:
        return self.config.api_key or os.getenv("OPENAI_API_KEY") or ""

    def _get_client(self):
        if self._aclient is None:
            try:
                from openai import AsyncOpenAI
                self._aclient = AsyncOpenAI(
                    api_key=self._get_api_key(),
                    base_url=self.config.base_url or None,
                )
            except ImportError:
                raise ImportError("openai library required. pip install openai")
        return self._aclient

    async def authenticate(self) -> str:
        client = self._get_client()
        try:
            await client.models.list()
            return "authenticated"
        except Exception as e:
            raise RuntimeError(f"OpenAI authentication failed: {e}")

    async def list_models(self) -> list[ModelInfo]:
        supported = [
            ModelInfo(id="gpt-4o", name="GPT-4o", provider="openai", capabilities=["chat", "vision"], context_window=128000, max_tokens=16384),
            ModelInfo(id="gpt-4o-mini", name="GPT-4o Mini", provider="openai", capabilities=["chat", "vision"], context_window=128000, max_tokens=16384),
            ModelInfo(id="gpt-4-turbo", name="GPT-4 Turbo", provider="openai", capabilities=["chat", "vision"], context_window=128000, max_tokens=4096),
            ModelInfo(id="gpt-4", name="GPT-4", provider="openai", capabilities=["chat"], context_window=8192, max_tokens=4096),
            ModelInfo(id="gpt-3.5-turbo", name="GPT-3.5 Turbo", provider="openai", capabilities=["chat"], context_window=16385, max_tokens=4096),
        ]
        try:
            client = self._get_client()
            resp = await client.models.list()
            remote_ids = {m.id for m in resp.data}
            for m in supported:
                m.available = m.id in remote_ids
        except Exception:
            pass
        return supported

    async def chat(self, messages: list[dict], config: dict[str, Any]) -> ChatResponse:
        client = self._get_client()
        model = config.get("model") or self.config.default_model or "gpt-4o"
        try:
            resp = await client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=config.get("temperature", 0.7),
                max_tokens=config.get("max_tokens", 2048),
            )
            choice = resp.choices[0]
            usage = Usage(
                prompt_tokens=resp.usage.prompt_tokens if resp.usage else 0,
                completion_tokens=resp.usage.completion_tokens if resp.usage else 0,
                total_tokens=resp.usage.total_tokens if resp.usage else 0,
            )
            return ChatResponse(
                id=resp.id,
                model=resp.model,
                choices=[Choice(index=choice.index, message=choice.message.model_dump(), finish_reason=choice.finish_reason)],
                usage=usage,
                provider="openai",
            )
        except Exception as e:
            return ChatResponse(
                id="fallback",
                model=model,
                choices=[Choice(index=0, message={"role": "assistant", "content": f"[OpenAI error: {e}]"})],
                provider="openai",
            )

    async def stream(self, messages: list[dict], config: dict[str, Any]) -> AsyncIterator[StreamChunk]:
        client = self._get_client()
        model = config.get("model") or self.config.default_model or "gpt-4o"
        try:
            stream = await client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=config.get("temperature", 0.7),
                max_tokens=config.get("max_tokens", 2048),
                stream=True,
                stream_options={"include_usage": True},
            )
            async for chunk in stream:
                delta = chunk.choices[0].delta if chunk.choices else None
                content = delta.content if delta else ""
                finish = chunk.choices[0].finish_reason if chunk.choices else None
                usage = None
                if chunk.usage:
                    usage = Usage(
                        prompt_tokens=chunk.usage.prompt_tokens or 0,
                        completion_tokens=chunk.usage.completion_tokens or 0,
                        total_tokens=chunk.usage.total_tokens or 0,
                    )
                yield StreamChunk(delta=content or "", finish_reason=finish, usage=usage, model=model)
        except Exception as e:
            yield StreamChunk(delta=f"[Stream error: {e}]", finish_reason="error")

    async def embeddings(self, texts: list[str]) -> list[list[float]]:
        client = self._get_client()
        model = self.config.options.get("embedding_model", "text-embedding-3-small")
        try:
            resp = await client.embeddings.create(model=model, input=texts)
            return [item.embedding for item in resp.data]
        except Exception:
            return [[0.0] * 1536 for _ in texts]

    async def health(self) -> HealthStatus:
        start = time.monotonic()
        try:
            client = self._get_client()
            await client.models.list()
            elapsed = (time.monotonic() - start) * 1000
            return HealthStatus(status="healthy", latency_ms=elapsed, last_check=datetime.now(timezone.utc))
        except Exception as e:
            elapsed = (time.monotonic() - start) * 1000
            return HealthStatus(status="unhealthy", latency_ms=elapsed, last_check=datetime.now(timezone.utc), error=str(e))

    async def limits(self) -> ProviderLimits:
        return ProviderLimits(max_requests_per_minute=500, max_tokens_per_minute=200000, max_concurrent_requests=50)

    async def pricing(self) -> PricingInfo:
        return PricingInfo(input_per_1k=0.01, output_per_1k=0.03, currency="USD")
