from __future__ import annotations

from typing import Any

from ..llm_models import ProviderInfo, ProviderState


class CapabilityRouter:
    """Routes to providers matching required capabilities."""

    async def route(self, request: Any, providers: list[ProviderInfo]) -> str | None:
        needed = getattr(request, "capabilities", [])
        if isinstance(request, dict):
            needed = request.get("capabilities", [])

        for p in providers:
            if p.state != ProviderState.ACTIVE:
                continue
            if not needed or all(cap in p.capabilities for cap in needed):
                return p.name
        return providers[0].name if providers else None
