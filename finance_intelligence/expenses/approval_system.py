"""Expense approval system for the Finance Intelligence Engine (Volume 35)."""

from __future__ import annotations

from typing import Any

from finance_intelligence.finance_events import (FinanceEventType,
                                                 FinanceEvents)
from finance_intelligence.finance_metrics import FinanceMetrics
from finance_intelligence.finance_models import (RiskLevel, Transaction,
                                                 TransactionStatus)
from finance_intelligence.finance_protocols import new_id
from finance_intelligence.finance_security import FinanceSecurity


class ApprovalSystem:
    """Approval workflow for expense reimbursements."""

    def __init__(self, events: FinanceEvents, metrics: FinanceMetrics,
                 security: FinanceSecurity | None = None) -> None:
        self.events = events
        self.metrics = metrics
        self.security = security or FinanceSecurity()
        self._requests: dict[str, dict[str, Any]] = {}

    def request(self, expense: Transaction,
                requester: str = "") -> dict[str, Any]:
        request = {
            "request_id": new_id("expense_request"),
            "transaction_id": expense.transaction_id,
            "requester": requester,
            "amount": expense.amount,
            "status": "pending",
        }
        if self.security.requires_approval(expense.amount,
                                           expense.risk_level):
            request["status"] = "approval_required"
            self.events.publish(FinanceEventType.APPROVAL_REQUIRED,
                                {"transaction_id": expense.transaction_id,
                                 "amount": expense.amount})
        else:
            request["status"] = "auto_approved"
            expense.status = TransactionStatus.APPROVED
            self.events.publish(FinanceEventType.TRANSACTION_APPROVED,
                                {"transaction_id": expense.transaction_id})
        self._requests[request["request_id"]] = request
        return request

    def approve(self, request_id: str, actor: str) -> bool:
        request = self._requests.get(request_id)
        if request is None or request["status"] != "approval_required":
            return False
        if not self.security.approve(actor):
            return False
        request["status"] = "approved"
        request["approved_by"] = actor
        self.metrics.increment("fi.expenses.approved")
        return True

    def reject(self, request_id: str, actor: str) -> bool:
        request = self._requests.get(request_id)
        if request is None or request["status"] != "approval_required":
            return False
        if not self.security.approve(actor):
            return False
        request["status"] = "rejected"
        request["rejected_by"] = actor
        return True

    def list(self) -> list[dict[str, Any]]:
        return list(self._requests.values())
