"""Payment approval flow for the Finance Intelligence Engine (V35)."""

from __future__ import annotations

from typing import Any

from finance_intelligence.finance_events import (FinanceEventType,
                                                 FinanceEvents)
from finance_intelligence.finance_metrics import FinanceMetrics
from finance_intelligence.finance_models import Payment, PaymentStatus
from finance_intelligence.finance_security import FinanceSecurity


class ApprovalFlow:
    """Approval workflow for scheduled payments."""

    def __init__(self, events: FinanceEvents, metrics: FinanceMetrics,
                 security: FinanceSecurity | None = None) -> None:
        self.events = events
        self.metrics = metrics
        self.security = security or FinanceSecurity()

    def request_approval(self, payment: Payment) -> bool:
        if payment.status != PaymentStatus.SCHEDULED:
            return False
        payment.status = PaymentStatus.APPROVAL_REQUIRED
        self.events.publish(FinanceEventType.APPROVAL_REQUIRED,
                            {"payment_id": payment.payment_id,
                             "amount": payment.amount})
        return True

    def requires_approval(self, payment: Payment) -> bool:
        return self.security.requires_approval(payment.amount,
                                               payment.risk_level)

    def approve(self, payment: Payment, actor: str) -> bool:
        if payment.status != PaymentStatus.APPROVAL_REQUIRED:
            return False
        if not self.security.approve(actor):
            self.security.audit_deny(actor, payment.payment_id)
            return False
        payment.status = PaymentStatus.APPROVED
        self.metrics.increment("fi.payments.approved")
        self.events.publish(FinanceEventType.PAYMENT_APPROVED,
                            {"payment_id": payment.payment_id,
                             "actor": actor})
        return True

    def reject(self, payment: Payment, actor: str) -> bool:
        if payment.status != PaymentStatus.APPROVAL_REQUIRED:
            return False
        if not self.security.approve(actor):
            return False
        payment.status = PaymentStatus.CANCELLED
        self.events.publish(FinanceEventType.APPROVAL_RESOLVED,
                            {"payment_id": payment.payment_id,
                             "actor": actor, "approved": False})
        return True
