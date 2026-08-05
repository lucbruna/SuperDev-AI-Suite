"""Budget analytics — analyzes budget variance and allocation."""
from __future__ import annotations

from typing import Any


class BudgetAnalytics:
    """Analyzes budget allocation breakdown."""

    def analyze(self, budget: dict[str, Any]) -> dict[str, Any]:
        total = budget.get("total", 0.0)
        if not total:
            return {"labor_pct": 0.0, "equipment_pct": 0.0, "post_pct": 0.0}
        return {
            "labor_pct": round(budget.get("labor", 0.0) / total * 100, 1),
            "equipment_pct": round(budget.get("equipment", 0.0) / total * 100, 1),
            "post_pct": round(budget.get("post", 0.0) / total * 100, 1),
        }


_budget_analytics: BudgetAnalytics | None = None


def get_budget_analytics() -> BudgetAnalytics:
    global _budget_analytics
    if _budget_analytics is None:
        _budget_analytics = BudgetAnalytics()
    return _budget_analytics
