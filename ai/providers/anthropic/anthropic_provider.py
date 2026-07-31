from __future__ import annotations

import os
import time
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Any

from ..base_provider import (
    BaseProvider,
    ChatResponse,
    Choice,
    HealthStatus,
    ModelInfo,
    PricingInfo,
    ProviderLimits,
    StreamChunk,
    Usage,
)


class AnthropicProvider(BaseProvider):
    def __init__(self, config: Any):
        super().__init__(config)
        self._client = None

    def _get_api_key(self) -> str:
        return self.config.api_key or os.getenv("ANTHROPIC_API_KEY") or ""

    def _get_client(self):
        if self._client is None:
            try:
                from anthropic import AsyncAnthropic

                self._client = AsyncAnthropic(
                    api_key=self._get_api_key(),
                    base_url=self.config.base_url or None,
                )
            except ImportError:
                raise ImportError("anthropic library required. pip install anthropic")
        return self._client

    async def authenticate(self) -> str:
        client = self._get_client()
        try:
            await client.models.list()
            return "authenticated"
        except Exception as e:
            raise RuntimeError(f"Anthropic authentication failed: {e}")

    async def list_models(self) -> list[ModelInfo]:
        return [
            ModelInfo(
                id="claude-3-5-sonnet-20241022",
                name="Claude 3.5 Sonnet",
                provider="anthropic",
                capabilities=["chat", "vision"],
                context_window=200000,
                max_tokens=8192,
            ),
            ModelInfo(
                id="claude-3-opus-20240229",
                name="Claude 3 Opus",
                provider="anthropic",
                capabilities=["chat", "vision"],
                context_window=200000,
                max_tokens=4096,
            ),
            ModelInfo(
                id="claude-3-haiku-20240307",
                name="Claude 3 Haiku",
                provider="anthropic",
                capabilities=["chat", "vision"],
                context_window=200000,
                max_tokens=4096,
            ),
            ModelInfo(
                id="claude-2.1",
                name="Claude 2.1",
                provider="anthropic",
                capabilities=["chat"],
                context_window=100000,
                max_tokens=4096,
            ),
        ]

    async def chat(self, messages: list[dict], config: dict[str, Any]) -> ChatResponse:
        client = self._get_client()
        model = config.get("model") or self.config.default_model or "claude-3-5-sonnet-20241022"
        system = None
        chat_messages = messages
        if messages and messages[0].get("role") == "system":
            system = messages[0]["content"]
            chat_messages = messages[1:]
        try:
            resp = await client.messages.create(
                model=model,
                messages=chat_messages,
                system=system,
                max_tokens=config.get("max_tokens", 2048),
                temperature=config.get("temperature", 0.7),
            )
            content = ""
            for block in resp.content:
                if block.type == "text":
                    content += block.text
            usage = Usage(
                prompt_tokens=resp.usage.input_tokens if resp.usage else 0,
                completion_tokens=resp.usage.output_tokens if resp.usage else 0,
                total_tokens=(resp.usage.input_tokens + resp.usage.output_tokens) if resp.usage else 0,
            )
            return ChatResponse(
                id=resp.id,
                model=resp.model,
                choices=[Choice(index=0, message={"role": "assistant", "content": content}, finish_reason="stop")],
                usage=usage,
                provider="anthropic",
            )
        except Exception as e:
            return ChatResponse(
                id="fallback",
                model=model,
                choices=[Choice(index=0, message={"role": "assistant", "content": f"[Anthropic error: {e}]"})],
                provider="anthropic",
            )

    async def stream(self, messages: list[dict], config: dict[str, Any]) -> AsyncIterator[StreamChunk]:
        client = self._get_client()
        model = config.get("model") or self.config.default_model or "claude-3-5-sonnet-20241022"
        system = None
        chat_messages = messages
        if messages and messages[0].get("role") == "system":
            system = messages[0]["content"]
            chat_messages = messages[1:]
        try:
            async with client.messages.stream(
                model=model,
                messages=chat_messages,
                system=system,
                max_tokens=config.get("max_tokens", 2048),
                temperature=config.get("temperature", 0.7),
            ) as stream:
                async for text in stream.text_stream:
                    yield StreamChunk(delta=text, model=model)
                final = await stream.get_final_message()
                usage = Usage(
                    prompt_tokens=final.usage.input_tokens if final.usage else 0,
                    completion_tokens=final.usage.output_tokens if final.usage else 0,
                    total_tokens=(final.usage.input_tokens + final.usage.output_tokens) if final.usage else 0,
                )
                yield StreamChunk(delta="", finish_reason="stop", usage=usage, model=model)
        except Exception as e:
            yield StreamChunk(delta=f"[Stream error: {e}]", finish_reason="error")

    async def embeddings(self, texts: list[str]) -> list[list[float]]:
        return [[0.0] * 768 for _ in texts]

    async def health(self) -> HealthStatus:
        start = time.monotonic()
        try:
            client = self._get_client()
            await client.models.list()
            elapsed = (time.monotonic() - start) * 1000
            return HealthStatus(status="healthy", latency_ms=elapsed, last_check=datetime.now(UTC))
        except Exception as e:
            elapsed = (time.monotonic() - start) * 1000
            return HealthStatus(status="unhealthy", latency_ms=elapsed, last_check=datetime.now(UTC), error=str(e))

    async def limits(self) -> ProviderLimits:
        return ProviderLimits(max_requests_per_minute=50, max_tokens_per_minute=100000, max_concurrent_requests=5)

    async def pricing(self) -> PricingInfo:
        return PricingInfo(input_per_1k=0.003, output_per_1k=0.015, currency="USD")
