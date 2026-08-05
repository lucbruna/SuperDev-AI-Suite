"""Budget manager — estimates production costs."""
from __future__ import annotations

from typing import Any

DAY_RATE = 1500.0


class BudgetManager:
    """Estimates budget from plan size and crew."""

    def estimate(self, plan: dict[str, Any], crew: int = 3) -> dict[str, Any]:
        days = max(1, (plan.get("scenes", 1) + 1) // 2)
        labor = days * crew * DAY_RATE
        equipment = days * 400.0
        post = 3000.0
        total = labor + equipment + post
        return {
            "labor": round(labor, 2),
            "equipment": round(equipment, 2),
            "post": post,
            "total": round(total, 2),
        }


_budget_manager: BudgetManager | None = None


def get_budget_manager() -> BudgetManager:
    global _budget_manager
    if _budget_manager is None:
        _budget_manager = BudgetManager()
    return _budget_manager
