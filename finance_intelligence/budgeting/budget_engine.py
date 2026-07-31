"""Budgeting subsystem facade (Volume 35).

Aggregates budget creation, monitoring, control and analysis.
"""

from __future__ import annotations

from typing import Any

from finance_intelligence.budgeting.budget_analysis import BudgetAnalysis
from finance_intelligence.budgeting.budget_control import BudgetControl
from finance_intelligence.budgeting.budget_manager import BudgetManager
from finance_intelligence.finance_events import FinanceEvents
from finance_intelligence.finance_metrics import FinanceMetrics


class BudgetEngine:
    """Aggregate facade over the budgeting subsystems."""

    def __init__(self, registry=None,
                 events: FinanceEvents | None = None,
                 metrics: FinanceMetrics | None = None) -> None:
        self.registry = registry
        self.events = events or FinanceEvents()
        self.metrics = metrics or FinanceMetrics()
        self.manager = BudgetManager(self.events, self.metrics)
        self.control = BudgetControl(self.manager)
        self.analysis = BudgetAnalysis(self.manager)

    # -- convenience ---------------------------------------------------------
    def create_budget(self, period: str, category: str,
                      planned: float, owner: str = ""):
        return self.manager.create(period, category, planned, owner)

    def record_spend(self, budget_id: str, amount: float) -> bool:
        return self.control.allow_spend(budget_id, amount)

    def monitor(self, budget_id: str) -> dict[str, Any]:
        budget = self.manager.get(budget_id)
        if budget is None:
            return {"status": "missing"}
        return self.manager.monitor(budget)

    def monitor_all(self) -> list[dict[str, Any]]:
        return self.analysis.variance_report()

    def stats(self) -> dict[str, Any]:
        summary = self.analysis.utilization_summary()
        return {
            "budgets": len(self.manager.list()),
            "summary": summary,
            "totals": self.analysis.totals(),
            "created": self.metrics.count("fi.budgets"),
        }
