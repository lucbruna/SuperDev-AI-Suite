"""Production analytics — holistic production-level metrics."""
from __future__ import annotations

from typing import Any


class ProductionAnalytics:
    """Combines plan, budget and schedule into a dashboard view."""

    def dashboard(self, result: dict[str, Any]) -> dict[str, Any]:
        plan = result.get("plan", {})
        budget = result.get("budget", {})
        schedule = result.get("schedule", {})
        team = result.get("team", {})
        return {
            "title": plan.get("title", ""),
            "scenes": plan.get("scenes", 0),
            "duration": plan.get("duration", 0.0),
            "total_cost": budget.get("total", 0.0),
            "days": schedule.get("days", 0),
            "crew": team.get("count", 0),
            "shots": result.get("shots", {}).get("count", 0),
        }


_production_analytics: ProductionAnalytics | None = None


def get_production_analytics() -> ProductionAnalytics:
    global _production_analytics
    if _production_analytics is None:
        _production_analytics = ProductionAnalytics()
    return _production_analytics
