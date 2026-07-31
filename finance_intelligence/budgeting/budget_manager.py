"""Budget management for the Finance Intelligence Engine (Volume 35)."""

from __future__ import annotations

from typing import Any

from finance_intelligence.finance_events import (FinanceEventType,
                                                 FinanceEvents)
from finance_intelligence.finance_interfaces import BudgetController
from finance_intelligence.finance_metrics import FinanceMetrics
from finance_intelligence.finance_models import Budget
from finance_intelligence.finance_protocols import new_id, now


class BudgetManager(BudgetController):
    """Create budgets and monitor utilization against actuals."""

    def __init__(self, events: FinanceEvents | None = None,
                 metrics: FinanceMetrics | None = None) -> None:
        self.events = events or FinanceEvents()
        self.metrics = metrics or FinanceMetrics()
        self._budgets: dict[str, Budget] = {}

    def create(self, period: str, category: str,
               planned: float, owner: str = "") -> Budget:
        budget = Budget(
            budget_id=new_id("budget"), period=period, category=category,
            planned=round(planned, 2), owner=owner, created_at=now())
        self._budgets[budget.budget_id] = budget
        self.metrics.increment("fi.budgets")
        self.events.publish(FinanceEventType.BUDGET_CREATED,
                            {"budget_id": budget.budget_id,
                             "period": period, "category": category})
        return budget

    def monitor(self, budget: Budget) -> dict[str, Any]:
        utilization = budget.utilization()
        variance = budget.variance()
        if utilization > 1.0:
            status = "over"
        elif utilization >= 0.8:
            status = "warning"
        else:
            status = "on_track"
        if utilization >= 0.8:
            self.events.publish(FinanceEventType.BUDGET_ALERT,
                                {"budget_id": budget.budget_id,
                                 "category": budget.category,
                                 "utilization": utilization})
        return {
            "budget_id": budget.budget_id,
            "period": budget.period,
            "category": budget.category,
            "planned": budget.planned,
            "actual": budget.actual,
            "variance": variance,
            "utilization": utilization,
            "status": status,
        }

    def get(self, budget_id: str) -> Budget | None:
        return self._budgets.get(budget_id)

    def list(self) -> list[Budget]:
        return list(self._budgets.values())

    def remove(self, budget_id: str) -> bool:
        return self._budgets.pop(budget_id, None) is not None
