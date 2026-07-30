from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime
from typing import Any


class PlannerMetrics:
    """Metrics collection for the planner module."""

    def __init__(self):
        self._counters: dict[str, int] = defaultdict(int)
        self._timings: dict[str, list[float]] = defaultdict(list)

    def increment(self, metric: str, value: int = 1) -> None:
        self._counters[metric] += value

    def record_timing(self, metric: str, duration: float) -> None:
        self._timings[metric].append(duration)

    def record_success(self) -> None:
        self.increment("tasks_succeeded")

    def record_failure(self) -> None:
        self.increment("tasks_failed")

    def snapshot(self) -> dict[str, Any]:
        return {
            "counters": dict(self._counters),
            "timing_counts": {k: len(v) for k, v in self._timings.items()},
            "timestamp": datetime.now(UTC).isoformat(),
        }
