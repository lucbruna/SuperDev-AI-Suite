"""Payment scheduling for the Finance Intelligence Engine (Volume 35)."""

from __future__ import annotations

import time
from typing import Any

from finance_intelligence.finance_events import (FinanceEventType,
                                                 FinanceEvents)
from finance_intelligence.finance_metrics import FinanceMetrics
from finance_intelligence.finance_models import (Payment, PaymentMethod,
                                                 PaymentStatus, RiskLevel)
from finance_intelligence.finance_protocols import new_id


class PaymentScheduler:
    """Schedule and track payments by due date."""

    def __init__(self, events: FinanceEvents,
                 metrics: FinanceMetrics) -> None:
        self.events = events
        self.metrics = metrics
        self._payments: dict[str, Payment] = {}

    def schedule(self, amount: float, method: PaymentMethod = PaymentMethod.PIX,
                 counterparty: str = "", due_date: float = 0.0,
                 risk_level: RiskLevel = RiskLevel.LOW) -> Payment:
        payment = Payment(
            payment_id=new_id("payment"), amount=round(amount, 2),
            method=method, counterparty=counterparty,
            status=PaymentStatus.SCHEDULED, due_date=due_date,
            risk_level=risk_level, created_at=time.time())
        self._payments[payment.payment_id] = payment
        self.metrics.increment("fi.payments.scheduled")
        self.events.publish(FinanceEventType.PAYMENT_SCHEDULED,
                            {"payment_id": payment.payment_id,
                             "amount": payment.amount})
        return payment

    def get(self, payment_id: str) -> Payment | None:
        return self._payments.get(payment_id)

    def list(self) -> list[Payment]:
        return list(self._payments.values())

    def list_scheduled(self) -> list[Payment]:
        return [payment for payment in self._payments.values()
                if payment.status == PaymentStatus.SCHEDULED]

    def due_between(self, start: float, end: float) -> list[Payment]:
        return [payment for payment in self._payments.values()
                if start <= payment.due_date <= end]

    def cancel(self, payment_id: str) -> bool:
        payment = self._payments.get(payment_id)
        if payment is None or payment.status == PaymentStatus.EXECUTED:
            return False
        payment.status = PaymentStatus.CANCELLED
        return True
