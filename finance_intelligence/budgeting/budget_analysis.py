"""Budget analysis for the Finance Intelligence Engine (Volume 35)."""

from __future__ import annotations

from typing import Any

from finance_intelligence.budgeting.budget_manager import BudgetManager
from finance_intelligence.finance_models import Budget
from finance_intelligence.finance_protocols import round_money, top_n


class BudgetAnalysis:
    """Report on variance and utilization across budgets."""

    def __init__(self, manager: BudgetManager) -> None:
        self.manager = manager

    def variance_report(self) -> list[dict[str, Any]]:
        return [self.manager.monitor(budget)
                for budget in self.manager.list()]

    def utilization_summary(self) -> dict[str, int]:
        summary = {"on_track": 0, "warning": 0, "over": 0}
        for report in self.variance_report():
            summary[report["status"]] += 1
        return summary

    def top_over_budget(self, limit: int = 5) -> list[Budget]:
        over = [budget for budget in self.manager.list()
                if budget.actual > budget.planned]
        return top_n(over,
                     key=lambda budget: budget.variance(), limit=limit)

    def totals(self) -> dict[str, float]:
        planned = round_money(
            sum(budget.planned for budget in self.manager.list()))
        actual = round_money(
            sum(budget.actual for budget in self.manager.list()))
        return {"planned": planned, "actual": actual,
                "variance": round_money(actual - planned)}
