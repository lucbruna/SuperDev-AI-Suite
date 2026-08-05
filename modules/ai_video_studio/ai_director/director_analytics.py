"""Director analytics — measures production performance and quality."""
from __future__ import annotations

from typing import Any


class DirectorAnalytics:
    """Computes summary metrics from direction results."""

    def summarize(self, result: dict[str, Any]) -> dict[str, Any]:
        plan = result.get("plan", {})
        budget = result.get("budget", {})
        schedule = result.get("schedule", {})
        return {
            "scenes": plan.get("scenes", 0),
            "duration": plan.get("duration", 0.0),
            "estimated_cost": budget.get("total", 0.0),
            "days": schedule.get("days", 0),
            "crew": result.get("team", {}).get("count", 0),
        }


_director_analytics: DirectorAnalytics | None = None


def get_director_analytics() -> DirectorAnalytics:
    global _director_analytics
    if _director_analytics is None:
        _director_analytics = DirectorAnalytics()
    return _director_analytics
