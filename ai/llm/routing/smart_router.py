from __future__ import annotations

from typing import Any

from ..llm_models import ProviderInfo, ProviderState


class SmartRouter:
    """Combines capability, latency, and cost heuristics for routing."""

    def __init__(
        self,
        latency_weight: float = 0.4,
        cost_weight: float = 0.3,
        capability_weight: float = 0.3,
    ) -> None:
        self._latency_weight = latency_weight
        self._cost_weight = cost_weight
        self._capability_weight = capability_weight

    async def route(self, request: Any, providers: list[ProviderInfo]) -> str | None:
        active = [p for p in providers if p.state == ProviderState.ACTIVE]
        if not active:
            return None

        needed = getattr(request, "capabilities", [])
        if isinstance(request, dict):
            needed = request.get("capabilities", [])

        scored: list[tuple[ProviderInfo, float]] = []
        max_latency = max(p.latency_p50 for p in active) or 1
        max_cost = max(p.cost_per_token for p in active) or 0.001

        for p in active:
            score = 0.0
            if needed and all(c in p.capabilities for c in needed):
                score += self._capability_weight
            elif not needed:
                score += self._capability_weight * 0.8

            norm_latency = 1 - (p.latency_p50 / max_latency)
            score += self._latency_weight * norm_latency

            norm_cost = 1 - (p.cost_per_token / max_cost)
            score += self._cost_weight * norm_cost

            scored.append((p, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[0][0].name if scored else None
