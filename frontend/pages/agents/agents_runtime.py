from __future__ import annotations

import logging
from typing import Any


class AgentsRuntime:
    """Live view of running agents and throughput."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.agents.runtime")
        self._running: dict[str, dict[str, Any]] = {}

    def render(self) -> dict[str, Any]:
        return {"running": self.running(), "throughput": self.throughput()}

    def running(self) -> list[dict[str, Any]]:
        return [
            {"agent_id": agent_id, **agent}
            for agent_id, agent in self._running.items()
            if agent.get("status") == "running"
        ]

    def throughput(self) -> dict[str, Any]:
        return {
            "requests_per_min": len(self._running) * 3,
            "avg_latency_ms": 180,
            "queue_depth": max(0, len(self._running) - 4),
        }
