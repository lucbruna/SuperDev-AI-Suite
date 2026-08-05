"""Performance analytics — measures production performance KPIs."""
from __future__ import annotations

from typing import Any


class PerformanceAnalytics:
    """Computes performance KPIs from production results."""

    def compute(self, result: dict[str, Any]) -> dict[str, Any]:
        plan = result.get("plan", {})
        budget = result.get("budget", {})
        schedule = result.get("schedule", {})
        total = budget.get("total", 0.0)
        return {
            "cost_per_scene": round(total / plan.get("scenes", 1), 2),
            "scenes_per_day": round(plan.get("scenes", 1) / schedule.get("days", 1), 2),
            "cost_per_minute": round(total / max(1.0, plan.get("duration", 1.0)), 2),
        }


_performance_analytics: PerformanceAnalytics | None = None


def get_performance_analytics() -> PerformanceAnalytics:
    global _performance_analytics
    if _performance_analytics is None:
        _performance_analytics = PerformanceAnalytics()
    return _performance_analytics
