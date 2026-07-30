from __future__ import annotations

from typing import Any

from ..llm_models import ProviderInfo, ProviderState


class CostRouter:
    """Routes to the cheapest provider."""

    async def route(self, request: Any, providers: list[ProviderInfo]) -> str | None:
        active = [p for p in providers if p.state == ProviderState.ACTIVE]
        if not active:
            return None
        return min(active, key=lambda p: p.cost_per_token).name
