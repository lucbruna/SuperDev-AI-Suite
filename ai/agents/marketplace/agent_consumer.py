"""Agent consumption and installation."""

from __future__ import annotations

from typing import Any


class AgentConsumer:
    """Handles searching and installing agents from the marketplace."""

    def __init__(self) -> None:
        self._installed: list[str] = []

    def search(self, query: dict[str, Any], listings: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
        category = query.get("category")
        keyword = query.get("keyword", "").lower()
        results: list[dict[str, Any]] = []
        for agent_id, spec in listings.items():
            if category and spec.get("category") != category:
                continue
            if keyword and keyword not in spec.get("name", "").lower():
                continue
            results.append({"id": agent_id, **spec})
        return results

    def install(self, agent_id: str, listings: dict[str, dict[str, Any]]) -> dict[str, Any]:
        if agent_id not in listings:
            return {"error": "Agent not found"}
        if agent_id in self._installed:
            return {"status": "already_installed"}
        self._installed.append(agent_id)
        return {"status": "installed", "agent_id": agent_id}

    def uninstall(self, agent_id: str) -> bool:
        if agent_id in self._installed:
            self._installed.remove(agent_id)
            return True
        return False

    def get_installed(self) -> list[str]:
        return list(self._installed)
