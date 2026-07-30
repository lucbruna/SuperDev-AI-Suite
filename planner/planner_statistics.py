from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime
from typing import Any


class PlannerStatistics:
    """Statistics and analytics for planner operations."""

    def __init__(self):
        self._stats: dict[str, Any] = {
            "plans_created": 0,
            "plans_completed": 0,
            "plans_failed": 0,
            "tasks_created": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "total_execution_time": 0.0,
        }
        self._daily: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    def increment(self, metric: str, value: int = 1) -> None:
        if metric in self._stats:
            self._stats[metric] += value
        today = datetime.now(UTC).strftime("%Y-%m-%d")
        self._daily[today][metric] += value

    def snapshot(self) -> dict[str, Any]:
        return {
            "totals": dict(self._stats),
            "daily": {k: dict(v) for k, v in self._daily.items()},
            "timestamp": datetime.now(UTC).isoformat(),
        }
