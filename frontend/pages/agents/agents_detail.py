from __future__ import annotations

import logging
from typing import Any


class AgentsDetail:
    """Agent detail view with info, logs and lifecycle controls."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.agents.detail")
        self._agents: dict[str, dict[str, Any]] = {}
        self._logs: dict[str, list[dict[str, Any]]] = {}

    def render(self, agent_id: str) -> dict[str, Any]:
        return {
            "agent_id": agent_id,
            "info": self.info(agent_id),
            "logs": self.logs(agent_id, limit=20),
        }

    def info(self, agent_id: str) -> dict[str, Any]:
        agent = self._agents.get(agent_id)
        if agent is None:
            raise KeyError(f"unknown agent: {agent_id}")
        return dict(agent)

    def logs(self, agent_id: str, limit: int = 100) -> list[dict[str, Any]]:
        entries = self._logs.get(agent_id, [])
        return entries[-limit:]

    def kill(self, agent_id: str) -> bool:
        agent = self._agents.get(agent_id)
        if agent is None:
            return False
        agent["status"] = "killed"
        return True
