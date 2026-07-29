from __future__ import annotations

from typing import Any


class WorkflowMetrics:
    _instance: WorkflowMetrics | None = None

    def __new__(cls) -> WorkflowMetrics:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.execution_counter = 0
            cls._instance.success_counter = 0
            cls._instance.failure_counter = 0
            cls._instance.duration_histogram: list[float] = []
        return cls._instance

    def increment_executions(self) -> None:
        self.execution_counter += 1

    def increment_success(self) -> None:
        self.success_counter += 1

    def increment_failure(self) -> None:
        self.failure_counter += 1

    def record_duration(self, duration_ms: float) -> None:
        self.duration_histogram.append(duration_ms)

    def snapshot(self) -> dict[str, Any]:
        durations = self.duration_histogram
        return {
            "total_executions": self.execution_counter,
            "total_success": self.success_counter,
            "total_failures": self.failure_counter,
            "duration_histogram_count": len(durations),
            "avg_duration_ms": sum(durations) / len(durations) if durations else 0.0,
            "min_duration_ms": min(durations) if durations else 0.0,
            "max_duration_ms": max(durations) if durations else 0.0,
        }
