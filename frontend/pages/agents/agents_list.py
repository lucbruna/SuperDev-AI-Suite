from __future__ import annotations

import logging
from typing import Any


class AgentsList:
    """Agent inventory with status and filtering."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.agents.list")
        self._agents: list[dict[str, Any]] = []

    def render(self) -> dict[str, Any]:
        return {"agents": list(self._agents), "count": len(self._agents)}

    def query(self, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        filters = filters or {}
        results = list(self._agents)
        for key, value in filters.items():
            if key in ("status", "type"):
                results = [a for a in results if a.get(key) == value]
        return results

    def sort(self, agents: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
        return sorted(agents, key=lambda a: str(a.get(key, "")))
