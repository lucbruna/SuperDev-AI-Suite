from __future__ import annotations

from collections.abc import AsyncIterator

from backend.providers.base_provider import (
    BaseProvider,
    CompletionResponse,
    EmbeddingResponse,
    Message,
    StreamChunk,
)
from backend.providers.provider_registry import ProviderRegistry


class AIRouter:
    """Intelligent router that selects the best provider for a request."""

    def __init__(self):
        self._fallback_order = ["openai", "anthropic", "ollama"]
        self._cost_budget: float | None = None
        self._preferred_provider: str | None = None

    def set_preferred_provider(self, provider: str | None) -> None:
        self._preferred_provider = provider

    def set_cost_budget(self, budget: float | None) -> None:
        self._cost_budget = budget

    async def _get_provider(self, provider_name: str | None = None) -> BaseProvider:
        name = provider_name or self._preferred_provider
        if name:
            return await ProviderRegistry.get_instance(name)

        for name in self._fallback_order:
            try:
                provider = await ProviderRegistry.get_instance(name)
                if await provider.health_check():
                    return provider
            except Exception:
                continue

        raise RuntimeError("No available LLM provider")

    async def complete(
        self,
        messages: list[Message],
        model: str | None = None,
        provider: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs,
    ) -> CompletionResponse:
        p = await self._get_provider(provider)
        model = model or p.supported_models[0]
        return await p.complete(messages, model, temperature, max_tokens, **kwargs)

    async def stream(
        self,
        messages: list[Message],
        model: str | None = None,
        provider: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs,
    ) -> AsyncIterator[StreamChunk]:
        p = await self._get_provider(provider)
        model = model or p.supported_models[0]
        async for chunk in p.stream(messages, model, temperature, max_tokens, **kwargs):
            yield chunk

    async def embed(
        self,
        texts: list[str],
        model: str | None = None,
        provider: str | None = None,
    ) -> EmbeddingResponse:
        p = await self._get_provider(provider)
        return await p.embed(texts, model)

    async def health_check_all(self) -> dict[str, bool]:
        results = {}
        for name in ProviderRegistry.list_providers():
            try:
                provider = await ProviderRegistry.get_instance(name)
                results[name] = await provider.health_check()
            except Exception:
                results[name] = False
        return results


router = AIRouter()
