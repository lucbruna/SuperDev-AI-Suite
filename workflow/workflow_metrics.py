from __future__ import annotations

import time
from typing import Any


class WorkflowMetrics:
    """Tracks workflow execution metrics."""

    def __init__(self) -> None:
        self._workflows_created = 0
        self._workflows_completed = 0
        self._workflows_failed = 0
        self._steps_executed = 0
        self._steps_failed = 0
        self._total_duration = 0.0

    def record_created(self) -> None:
        self._workflows_created += 1

    def record_completed(self, duration: float) -> None:
        self._workflows_completed += 1
        self._total_duration += duration

    def record_failed(self) -> None:
        self._workflows_failed += 1

    def record_step_executed(self) -> None:
        self._steps_executed += 1

    def record_step_failed(self) -> None:
        self._steps_failed += 1

    def snapshot(self) -> dict[str, Any]:
        return {
            "workflows_created": self._workflows_created,
            "workflows_completed": self._workflows_completed,
            "workflows_failed": self._workflows_failed,
            "steps_executed": self._steps_executed,
            "steps_failed": self._steps_failed,
            "total_duration": round(self._total_duration, 3),
            "timestamp": time.time(),
        }
