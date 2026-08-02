from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from backend.config import config
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

    async def _provider_kwargs(self, name: str, db: Any | None = None) -> dict:
        """Pass configured settings (base_url/model/keys) when building a provider.

        Env-var config from ``config.providers`` is used as the baseline. When
        a DB session is provided, any provider saved through the Settings UI
        (api key / base URL / first model) is overlaid on top so the runtime
        honors the UI configuration. Errors degrade silently to env defaults.
        """
        providers = config.providers
        if name == "ollama":
            kwargs: dict[str, Any] = {
                "base_url": providers.ollama_base_url or "http://localhost:11434",
                "model": providers.ollama_model or "llama3.1",
            }
        elif name == "openai":
            kwargs = {
                "api_key": providers.openai_api_key or None,
                "base_url": providers.openai_base_url,
                "model": providers.openai_model,
            }
        elif name == "anthropic":
            kwargs = {
                "api_key": providers.anthropic_api_key or None,
                "base_url": providers.anthropic_base_url,
                "model": providers.anthropic_model,
            }
        else:
            kwargs = {}

        if db is not None:
            try:
                from backend.services.settings_service import get_runtime_provider_config

                saved = await get_runtime_provider_config(db, name)
                if saved.get("api_key"):
                    kwargs["api_key"] = saved["api_key"]
                if saved.get("base_url"):
                    kwargs["base_url"] = saved["base_url"]
                if saved.get("model"):
                    kwargs["model"] = saved["model"]
            except Exception:
                # Settings table unavailable (e.g. migrations not run yet) —
                # fall back to env defaults.
                pass

        return kwargs

    async def _get_provider(
        self, provider_name: str | None = None, db: Any | None = None
    ) -> BaseProvider:
        name = provider_name or self._preferred_provider
        if name:
            return await ProviderRegistry.get_instance(name, **await self._provider_kwargs(name, db))

        for name in self._fallback_order:
            try:
                provider = await ProviderRegistry.get_instance(
                    name, **await self._provider_kwargs(name, db)
                )
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
        db: Any | None = None,
        **kwargs,
    ) -> CompletionResponse:
        p = await self._get_provider(provider, db)
        model = model or p.supported_models[0]
        return await p.complete(messages, model, temperature, max_tokens, **kwargs)

    async def stream(
        self,
        messages: list[Message],
        model: str | None = None,
        provider: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        db: Any | None = None,
        **kwargs,
    ) -> AsyncIterator[StreamChunk]:
        p = await self._get_provider(provider, db)
        model = model or p.supported_models[0]
        async for chunk in p.stream(messages, model, temperature, max_tokens, **kwargs):
            yield chunk

    async def embed(
        self,
        texts: list[str],
        model: str | None = None,
        provider: str | None = None,
        db: Any | None = None,
    ) -> EmbeddingResponse:
        p = await self._get_provider(provider, db)
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
