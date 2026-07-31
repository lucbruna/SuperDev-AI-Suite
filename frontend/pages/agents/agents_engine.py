from __future__ import annotations

import logging
import time
from typing import Any

from ...frontend_context import FrontendContext


class AgentsEngine:
    """Renders the agent management and orchestration page."""

    def __init__(self, context: FrontendContext | None = None) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.agents")
        self._context = context or FrontendContext()
        self._agents: dict[str, dict[str, Any]] = {}

    def render(self, **kwargs: Any) -> dict[str, Any]:
        return {
            "page": "agents",
            "count": len(self._agents),
            "agents": self.list(),
        }

    def list(self) -> list[dict[str, Any]]:
        return [
            {"agent_id": agent_id, **agent}
            for agent_id, agent in self._agents.items()
        ]

    def spawn(self, agent_type: str, config: dict[str, Any] | None = None) -> str:
        agent_id = f"agent-{len(self._agents) + 1}"
        self._agents[agent_id] = {
            "type": agent_type,
            "config": config or {},
            "status": "spawning",
            "created_at": time.time(),
        }
        return agent_id

    def stop(self, agent_id: str) -> bool:
        agent = self._agents.get(agent_id)
        if agent is None:
            return False
        agent["status"] = "stopped"
        return True

    def status(self, agent_id: str) -> dict[str, Any]:
        agent = self._agents.get(agent_id)
        if agent is None:
            raise KeyError(f"unknown agent: {agent_id}")
        return {"agent_id": agent_id, **agent}
