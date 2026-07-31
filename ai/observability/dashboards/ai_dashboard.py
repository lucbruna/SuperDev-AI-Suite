"""AI dashboard."""
from __future__ import annotations

from typing import Any


class AIDashboard:
    def __init__(self) -> None:
        self._agent_metrics: dict[str, dict[str, Any]] = {}
        self._model_metrics: dict[str, dict[str, Any]] = {}
    def update_agent_metrics(self, agent_id: str, metrics: dict[str, Any]) -> None:
        self._agent_metrics[agent_id] = metrics
    def update_model_metrics(self, model_id: str, metrics: dict[str, Any]) -> None:
        self._model_metrics[model_id] = metrics
    def get_agent_status(self, agent_id: str) -> dict[str, Any]:
        return self._agent_metrics.get(agent_id, {})
    def get_model_performance(self, model_id: str) -> dict[str, Any]:
        return self._model_metrics.get(model_id, {})
    def get_active_agents(self) -> list[str]:
        return [k for k, v in self._agent_metrics.items() if v.get("status") == "active"]
    def get_model_usage(self) -> dict[str, int]:
        return {k: v.get("calls", 0) for k, v in self._model_metrics.items()}
    def get_summary(self) -> dict[str, Any]:
        return {"agents": len(self._agent_metrics), "models": len(self._model_metrics), "active": len(self.get_active_agents())}
