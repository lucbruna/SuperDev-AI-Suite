"""Behavior optimization from evaluation signals (Volume 31)."""

from __future__ import annotations

from typing import Any

from agent_orchestration.orchestrator_models import EvaluationReport


class BehaviorOptimizer:
    """Adjusts agent behavior parameters based on evaluation reports."""

    def __init__(self, params: dict[str, Any] | None = None) -> None:
        self.params = params or {"max_retries": 3, "timeout": 10.0,
                                 "risk_tolerance": 0.5}
        self._history: list[dict[str, Any]] = []

    def apply(self, report: EvaluationReport) -> dict[str, Any]:
        changes: dict[str, Any] = {}
        if report.quality_score < 0.5:
            retries = self.params.get("max_retries", 3)
            changes["max_retries"] = min(retries + 1, 5)
        if report.avg_time > 5.0:
            timeout = self.params.get("timeout", 10.0)
            changes["timeout"] = min(timeout * 1.5, 60.0)
        if report.errors > 0:
            tolerance = self.params.get("risk_tolerance", 0.5)
            changes["risk_tolerance"] = max(tolerance - 0.1, 0.0)
        for key, value in changes.items():
            self.params[key] = value
        if changes:
            self._history.append({"agent_id": report.agent_id,
                                  "changes": dict(changes),
                                  "quality_score": report.quality_score})
        return changes

    def history(self) -> list[dict[str, Any]]:
        return list(self._history)

    def count(self) -> int:
        return len(self._history)
