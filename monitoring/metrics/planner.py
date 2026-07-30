from __future__ import annotations

from typing import Any

from ..monitoring_models import MetricSample, MetricType


class PlannerMetrics:
    """Metrics collector for the planner engine."""

    def __init__(self) -> None:
        self._plans_created: int = 0
        self._plans_completed: int = 0
        self._plans_failed: int = 0

    def record_plan(self, action: str) -> list[MetricSample]:
        if action == "create":
            self._plans_created += 1
        elif action == "complete":
            self._plans_completed += 1
        elif action == "fail":
            self._plans_failed += 1
        return [
            MetricSample("planner_plans_created", float(self._plans_created), metric_type=MetricType.GAUGE),
            MetricSample("planner_plans_completed", float(self._plans_completed), metric_type=MetricType.GAUGE),
            MetricSample("planner_plans_failed", float(self._plans_failed), metric_type=MetricType.GAUGE),
        ]

    def snapshot(self) -> dict[str, Any]:
        return {
            "created": self._plans_created,
            "completed": self._plans_completed,
            "failed": self._plans_failed,
        }


__all__ = ["PlannerMetrics"]
