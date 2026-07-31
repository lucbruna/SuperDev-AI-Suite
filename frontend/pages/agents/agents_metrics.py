from __future__ import annotations

import logging
from typing import Any


class AgentsMetrics:
    """Agent performance and usage metrics."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.agents.metrics")
        self._samples: dict[str, list[dict[str, Any]]] = {}

    def render(self) -> dict[str, Any]:
        return {"overview": self.overview(), "by_agent": len(self._samples)}

    def overview(self, period: str = "7d") -> dict[str, Any]:
        return {
            "period": period,
            "total_runs": sum(len(samples) for samples in self._samples.values()),
            "agents": len(self._samples),
            "success_rate": 0.95,
        }

    def by_agent(self, agent_id: str) -> dict[str, Any]:
        samples = self._samples.get(agent_id, [])
        return {
            "agent_id": agent_id,
            "runs": len(samples),
            "tokens": sum(int(s.get("tokens", 0)) for s in samples),
            "duration_ms": sum(int(s.get("duration_ms", 0)) for s in samples),
        }
