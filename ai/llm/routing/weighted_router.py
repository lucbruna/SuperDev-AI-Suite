from __future__ import annotations

import random
from typing import Any

from ..llm_models import ProviderInfo, ProviderState


class WeightedRouter:
    """Weighted random selection router."""

    def __init__(self) -> None:
        self._weights: dict[str, float] = {}

    def set_weight(self, provider: str, weight: float) -> None:
        self._weights[provider] = weight

    async def route(self, request: Any, providers: list[ProviderInfo]) -> str | None:
        active = [p for p in providers if p.state == ProviderState.ACTIVE]
        if not active:
            return None
        weights = [self._weights.get(p.name, 1.0) for p in active]
        total = sum(weights)
        if total <= 0:
            return active[0].name
        r = random.uniform(0, total)
        cumulative = 0.0
        for i, p in enumerate(active):
            cumulative += weights[i]
            if r <= cumulative:
                return p.name
        return active[-1].name
