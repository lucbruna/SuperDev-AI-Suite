"""Expenses subsystem facade (Volume 35).

Aggregates category management, approval workflow, expense analysis and
cost optimization.
"""

from __future__ import annotations

from typing import Any

from finance_intelligence.expenses.approval_system import ApprovalSystem
from finance_intelligence.expenses.category_manager import CategoryManager
from finance_intelligence.expenses.cost_optimizer import CostOptimizer
from finance_intelligence.expenses.expense_analysis import ExpenseAnalysis
from finance_intelligence.finance_events import FinanceEvents
from finance_intelligence.finance_metrics import FinanceMetrics
from finance_intelligence.finance_models import (RiskLevel, Transaction,
                                                 TransactionType)
from finance_intelligence.finance_protocols import new_id
from finance_intelligence.finance_registry import FinanceRegistry
from finance_intelligence.finance_security import FinanceSecurity


class ExpenseEngine:
    """Aggregate facade over the expenses subsystems."""

    def __init__(self, registry: FinanceRegistry | None = None,
                 events: FinanceEvents | None = None,
                 metrics: FinanceMetrics | None = None,
                 security: FinanceSecurity | None = None) -> None:
        self.registry = registry or FinanceRegistry()
        self.events = events or FinanceEvents()
        self.metrics = metrics or FinanceMetrics()
        self.security = security or FinanceSecurity()
        self.categories = CategoryManager()
        self.approvals = ApprovalSystem(self.events, self.metrics,
                                        self.security)
        self.analysis = ExpenseAnalysis()
        self.optimizer = CostOptimizer()

    # -- convenience ---------------------------------------------------------
    def register_expense(self, description: str, amount: float,
                         category: str = "", requester: str = "",
                         risk_level: RiskLevel = RiskLevel.LOW):
        category_id = category or self.categories.classify(description)
        expense = Transaction(
            transaction_id=new_id("expense"),
            kind=TransactionType.EXPENSE, amount=round(amount, 2),
            risk_level=risk_level, description=description,
            metadata={"category_id": category_id, "month": "2026-01"})
        self.registry.register_transaction(expense)
        self.metrics.increment("fi.expenses")
        return expense

    def request_approval(self, expense: Transaction, requester: str = ""):
        return self.approvals.request(expense, requester)

    def spending_by_category(self) -> dict[str, float]:
        return self.categories.spending_by_category(
            self.registry.list_transactions())

    def suggestions(self) -> list[dict[str, Any]]:
        categories = {category["category_id"]: category
                      for category in self.categories.list()}
        return self.optimizer.suggestions(
            self.registry.list_transactions(), categories)

    def stats(self) -> dict[str, Any]:
        transactions = self.registry.list_transactions()
        return {
            "expenses": len(transactions),
            "total": round(
                sum(tx.amount for tx in transactions), 2),
            "approval_requests": len(self.approvals.list()),
        }
