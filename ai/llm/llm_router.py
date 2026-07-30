from __future__ import annotations

import random
from typing import Any

from .llm_interfaces import ILLMRouter
from .llm_models import ProviderInfo, ProviderState
from .llm_registry import LLMRegistry


class LLMRouter(ILLMRouter):
    """Routes LLM requests based on strategy."""

    STRATEGY_CAPABILITY = "capability"
    STRATEGY_LATENCY = "latency"
    STRATEGY_COST = "cost"
    STRATEGY_QUALITY = "quality"
    STRATEGY_AVAILABILITY = "availability"
    STRATEGY_WEIGHTED = "weighted"
    STRATEGY_PRIORITY = "priority"
    STRATEGY_SMART = "smart"
    STRATEGY_FALLBACK = "fallback"

    def __init__(self, registry: LLMRegistry) -> None:
        self._registry = registry
        self._weights: dict[str, float] = {}
        self._priorities: dict[str, int] = {}

    async def select_provider(
        self,
        strategy: str,
        requirements: dict[str, Any] | None = None,
    ) -> str | None:
        providers = self._get_candidates(requirements or {})
        if not providers:
            return None

        strategy_map = {
            self.STRATEGY_CAPABILITY: self._select_by_capability,
            self.STRATEGY_LATENCY: self._select_by_latency,
            self.STRATEGY_COST: self._select_by_cost,
            self.STRATEGY_QUALITY: self._select_by_quality,
            self.STRATEGY_AVAILABILITY: self._select_by_availability,
            self.STRATEGY_WEIGHTED: self._select_by_weighted,
            self.STRATEGY_PRIORITY: self._select_by_priority,
            self.STRATEGY_SMART: self._select_smart,
            self.STRATEGY_FALLBACK: self._select_fallback,
        }

        selector = strategy_map.get(strategy)
        if selector is None:
            return providers[0].name

        return await selector(providers, requirements or {})

    def set_weight(self, provider: str, weight: float) -> None:
        self._weights[provider] = weight

    def set_priority(self, provider: str, priority: int) -> None:
        self._priorities[provider] = priority

    def _get_candidates(self, requirements: dict[str, Any]) -> list[ProviderInfo]:
        candidates: list[ProviderInfo] = []
        for name in self._registry.list_names():
            info = self._registry.get_info(name)
            if info and info.state == ProviderState.ACTIVE:
                candidates.append(info)
        return candidates

    async def _select_by_capability(
        self, providers: list[ProviderInfo], requirements: dict[str, Any]
    ) -> str | None:
        needed = requirements.get("capabilities", [])
        for p in providers:
            if all(cap in p.capabilities for cap in needed):
                return p.name
        return providers[0].name if providers else None

    async def _select_by_latency(
        self, providers: list[ProviderInfo], requirements: dict[str, Any]
    ) -> str | None:
        if not providers:
            return None
        return min(providers, key=lambda p: p.latency_p50).name

    async def _select_by_cost(
        self, providers: list[ProviderInfo], requirements: dict[str, Any]
    ) -> str | None:
        if not providers:
            return None
        return min(providers, key=lambda p: p.cost_per_token).name

    async def _select_by_quality(
        self, providers: list[ProviderInfo], requirements: dict[str, Any]
    ) -> str | None:
        for p in providers:
            if "quality" in p.capabilities:
                return p.name
        return providers[0].name if providers else None

    async def _select_by_availability(
        self, providers: list[ProviderInfo], requirements: dict[str, Any]
    ) -> str | None:
        return providers[0].name if providers else None

    async def _select_by_weighted(
        self, providers: list[ProviderInfo], requirements: dict[str, Any]
    ) -> str | None:
        if not providers:
            return None
        weights = [self._weights.get(p.name, 1.0) for p in providers]
        total = sum(weights)
        if total <= 0:
            return providers[0].name
        r = random.uniform(0, total)
        cumulative = 0.0
        for i, p in enumerate(providers):
            cumulative += weights[i]
            if r <= cumulative:
                return p.name
        return providers[-1].name

    async def _select_by_priority(
        self, providers: list[ProviderInfo], requirements: dict[str, Any]
    ) -> str | None:
        if not providers:
            return None
        return max(providers, key=lambda p: self._priorities.get(p.name, 0)).name

    async def _select_smart(
        self, providers: list[ProviderInfo], requirements: dict[str, Any]
    ) -> str | None:
        needed = requirements.get("capabilities", [])
        for p in providers:
            if all(cap in p.capabilities for cap in needed):
                if p.latency_p50 < 1000 and p.cost_per_token < 0.01:
                    return p.name
        return providers[0].name if providers else None

    async def _select_fallback(
        self, providers: list[ProviderInfo], requirements: dict[str, Any]
    ) -> str | None:
        return providers[0].name if providers else None

    async def select(self, prompt: str, **kwargs: Any) -> str:
        strategy = kwargs.pop("strategy", self.STRATEGY_FALLBACK)
        requirements = kwargs.pop("requirements", {})
        result = await self.select_provider(strategy=strategy, requirements=requirements)
        if result is None:
            raise RuntimeError("No available provider for routing")
        return result
