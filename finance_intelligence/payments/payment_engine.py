"""Payments subsystem facade (Volume 35).

Aggregates payment scheduling, approval flow, gateway execution and
fraud detection.
"""

from __future__ import annotations

from typing import Any

from finance_intelligence.finance_events import FinanceEvents
from finance_intelligence.finance_metrics import FinanceMetrics
from finance_intelligence.finance_models import (PaymentMethod, RiskLevel)
from finance_intelligence.finance_registry import FinanceRegistry
from finance_intelligence.finance_security import FinanceSecurity
from finance_intelligence.payments.approval_flow import ApprovalFlow
from finance_intelligence.payments.fraud_detection import FraudDetection
from finance_intelligence.payments.payment_gateway import PaymentGateway
from finance_intelligence.payments.payment_scheduler import (
    PaymentScheduler)


class PaymentEngine:
    """Aggregate facade over the payments subsystems."""

    def __init__(self, registry: FinanceRegistry | None = None,
                 events: FinanceEvents | None = None,
                 metrics: FinanceMetrics | None = None,
                 security: FinanceSecurity | None = None) -> None:
        self.registry = registry or FinanceRegistry()
        self.events = events or FinanceEvents()
        self.metrics = metrics or FinanceMetrics()
        self.security = security or FinanceSecurity()
        self.scheduler = PaymentScheduler(self.events, self.metrics)
        self.approvals = ApprovalFlow(self.events, self.metrics,
                                      self.security)
        self.gateway = PaymentGateway(self.events, self.metrics)
        self.fraud = FraudDetection(self.events, self.metrics)

    # -- convenience flow ----------------------------------------------------
    def schedule_payment(self, amount: float,
                         method: PaymentMethod = PaymentMethod.PIX,
                         counterparty: str = "",
                         due_date: float = 0.0,
                         risk_level: RiskLevel = RiskLevel.LOW):
        payment = self.scheduler.schedule(
            amount, method, counterparty, due_date, risk_level)
        if self.approvals.requires_approval(payment):
            self.approvals.request_approval(payment)
        return payment

    def approve(self, payment_id: str, actor: str) -> bool:
        payment = self.scheduler.get(payment_id)
        if payment is None:
            return False
        return self.approvals.approve(payment, actor)

    def reject(self, payment_id: str, actor: str) -> bool:
        payment = self.scheduler.get(payment_id)
        if payment is None:
            return False
        return self.approvals.reject(payment, actor)

    def execute(self, payment_id: str) -> dict[str, Any]:
        payment = self.scheduler.get(payment_id)
        if payment is None:
            return {"payment_id": payment_id, "status": "not_found"}
        check = self.fraud.analyze(payment)
        if check["flagged"]:
            return {"payment_id": payment_id, "status": "blocked",
                    "fraud": check}
        return self.gateway.execute(payment)

    def stats(self) -> dict[str, Any]:
        return {
            "scheduled": len(self.scheduler.list_scheduled()),
            "executed": len(self.gateway.history()),
            "approved": self.metrics.count("fi.payments.approved"),
            "fraud_flagged": self.metrics.count("fi.fraud.flagged"),
        }
