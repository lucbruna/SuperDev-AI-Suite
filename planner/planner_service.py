from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .planner_metrics import PlannerMetrics
from .planner_validator import PlannerValidator


class PlannerService:
    """Services for plan management and orchestration."""

    def __init__(self):
        self.validator = PlannerValidator()
        self.metrics = PlannerMetrics()
        self._service_history: list[dict[str, Any]] = []

    def validate_plan(self, plan: Any) -> dict[str, Any]:
        return self.validator.validate(plan)

    def estimate_duration(self, plan: Any) -> float:
        return self.validator.estimate_duration(plan)

    def get_statistics(self) -> dict[str, Any]:
        return self.metrics.snapshot()

    def record_event(self, event_type: str, data: dict[str, Any]) -> None:
        self._service_history.append({
            "type": event_type,
            "data": data,
            "timestamp": datetime.now(UTC).isoformat(),
        })
