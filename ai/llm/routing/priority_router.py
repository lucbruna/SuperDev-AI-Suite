from __future__ import annotations

from typing import Any

from ..llm_models import ProviderInfo, ProviderState


class PriorityRouter:
    """Priority-based routing."""

    def __init__(self) -> None:
        self._priorities: dict[str, int] = {}

    def set_priority(self, provider: str, priority: int) -> None:
        self._priorities[provider] = priority

    async def route(self, request: Any, providers: list[ProviderInfo]) -> str | None:
        active = [p for p in providers if p.state == ProviderState.ACTIVE]
        if not active:
            return None
        return max(active, key=lambda p: self._priorities.get(p.name, 0)).name
