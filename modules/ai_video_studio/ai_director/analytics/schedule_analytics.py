"""Schedule analytics — analyzes timeline efficiency."""
from __future__ import annotations

from typing import Any


class ScheduleAnalytics:
    """Analyzes schedule utilization."""

    def analyze(self, schedule: dict[str, Any]) -> dict[str, Any]:
        days = schedule.get("days", 1)
        scenes = schedule.get("scenes_per_day", 0)
        return {"total_days": days, "utilization": round(min(1.0, scenes / 2), 3)}


_schedule_analytics: ScheduleAnalytics | None = None


def get_schedule_analytics() -> ScheduleAnalytics:
    global _schedule_analytics
    if _schedule_analytics is None:
        _schedule_analytics = ScheduleAnalytics()
    return _schedule_analytics
