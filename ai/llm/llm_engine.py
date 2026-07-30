from __future__ import annotations

import time
import uuid
from typing import Any

from .llm_cache import LLMCache
from .llm_context import LLMContextBuilder
from .llm_executor import LLMExecutor
from .llm_factory import LLMFactory
from .llm_manager import LLMManager
from .llm_models import LLMResponse
from .llm_router import LLMRouter


class LLMEngine:
    """Unified engine for LLM operations."""

    def __init__(self, manager: LLMManager | None = None) -> None:
        self._manager = manager or LLMManager()
        self._logger = self._manager.logger
        self._metrics = self._manager.metrics
        self._registry = self._manager.registry
        self._router = self._manager.router
        self._cache = LLMCache()
        self._context_manager = LLMContextBuilder()
        self._executor = LLMExecutor(self._registry, self._metrics, self._logger)
        self._factory = LLMFactory()

    @property
    def manager(self) -> LLMManager:
        return self._manager

    async def execute(
        self,
        prompt: str,
        provider: str | None = None,
        model: str | None = None,
        strategy: str = LLMRouter.STRATEGY_FALLBACK,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        cache_key: str | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        start = time.time()
        request_id = str(uuid.uuid4())

        if cache_key:
            cached = await self._cache.get(cache_key)
            if cached:
                self._logger.info(provider or "unknown", "Cache hit")
                return LLMResponse(
                    request_id=request_id,
                    provider=cached.get("provider", ""),
                    model=cached.get("model", ""),
                    content=cached.get("content", ""),
                    tokens_prompt=cached.get("tokens_prompt", 0),
                    tokens_completion=cached.get("tokens_completion", 0),
                    finish_reason="cache",
                )

        resolved_provider = provider
        if not resolved_provider:
            selected = await self._router.select(
                prompt,
                strategy=strategy,
                requirements=kwargs.pop("requirements", {}),
            )
            resolved_provider = selected

        resolved_model = model or ""

        raw = await self._executor.execute(
            resolved_provider, prompt, max_tokens=max_tokens, temperature=temperature, **kwargs
        )

        latency = (time.time() - start) * 1000

        response = LLMResponse(
            request_id=request_id,
            provider=resolved_provider,
            model=resolved_model,
            content=raw.get("content", ""),
            tokens_prompt=raw.get("tokens_prompt", 0),
            tokens_completion=raw.get("tokens_completion", 0),
            latency_ms=round(latency, 2),
            cost_usd=raw.get("cost_usd", 0.0),
            finish_reason=raw.get("finish_reason", "stop"),
        )

        if cache_key:
            await self._cache.set(cache_key, raw)

        return response

    async def execute_with_fallback(
        self,
        prompt: str,
        providers: list[str],
        model: str | None = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> LLMResponse:
        errors: list[str] = []
        for provider in providers:
            try:
                return await self.execute(
                    prompt=prompt,
                    provider=provider,
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    **kwargs,
                )
            except Exception as e:
                errors.append(f"{provider}: {e}")
                continue
        raise RuntimeError(f"All providers failed: {'; '.join(errors)}")

    def get_cache_info(self) -> dict[str, Any]:
        return self._cache.to_dict()

    async def clear_cache(self) -> None:
        await self._cache.clear()

    async def health_check(self) -> dict[str, Any]:
        return await self._manager.health_check()

    def to_dict(self) -> dict[str, Any]:
        return {
            "manager": self._manager.to_dict(),
            "cache": self.get_cache_info(),
        }
