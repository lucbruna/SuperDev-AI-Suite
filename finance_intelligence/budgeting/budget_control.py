"""Budget control for the Finance Intelligence Engine (Volume 35)."""

from __future__ import annotations

from typing import Any

from finance_intelligence.budgeting.budget_manager import BudgetManager
from finance_intelligence.finance_models import Budget
from finance_intelligence.finance_protocols import round_money


class BudgetControl:
    """Gate spending against budget headroom."""

    def __init__(self, manager: BudgetManager) -> None:
        self.manager = manager

    def remaining(self, budget: Budget) -> float:
        return round_money(budget.planned - budget.actual)

    def can_spend(self, budget: Budget, amount: float) -> bool:
        return self.remaining(budget) >= amount

    def allow_spend(self, budget_id: str, amount: float) -> bool:
        budget = self.manager.get(budget_id)
        if budget is None or not self.can_spend(budget, amount):
            return False
        budget.actual = round_money(budget.actual + amount)
        return True

    def over_budgets(self) -> list[Budget]:
        return [budget for budget in self.manager.list()
                if budget.actual > budget.planned]
