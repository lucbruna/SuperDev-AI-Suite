"""Payment gateway integration for the Finance Intelligence Engine (V35).

Simulated provider execution for PIX, boleto, card and transfers.
"""

from __future__ import annotations

import time
from typing import Any

from finance_intelligence.finance_events import (FinanceEventType,
                                                 FinanceEvents)
from finance_intelligence.finance_metrics import FinanceMetrics
from finance_intelligence.finance_models import Payment, PaymentStatus


class PaymentGateway:
    """Executes approved payments through a provider channel."""

    def __init__(self, events: FinanceEvents,
                 metrics: FinanceMetrics) -> None:
        self.events = events
        self.metrics = metrics
        self._executed: dict[str, dict[str, Any]] = {}

    def execute(self, payment: Payment) -> dict[str, Any]:
        if payment.status != PaymentStatus.APPROVED:
            return {"payment_id": payment.payment_id,
                    "status": "not_approved"}
        provider = payment.method.value
        payment.status = PaymentStatus.EXECUTED
        record = {
            "payment_id": payment.payment_id,
            "provider": provider,
            "amount": payment.amount,
            "processed_at": time.time(),
            "status": "executed",
        }
        self._executed[payment.payment_id] = record
        self.metrics.increment("fi.payments.executed")
        self.events.publish(FinanceEventType.PAYMENT_EXECUTED,
                            {"payment_id": payment.payment_id,
                             "provider": provider})
        return record

    def fail(self, payment: Payment, reason: str = "") -> dict[str, Any]:
        payment.status = PaymentStatus.FAILED
        record = {"payment_id": payment.payment_id, "status": "failed",
                  "reason": reason}
        self._executed[payment.payment_id] = record
        self.metrics.increment("fi.payments.failed")
        self.events.publish(FinanceEventType.PAYMENT_FAILED,
                            {"payment_id": payment.payment_id,
                             "reason": reason})
        return record

    def history(self) -> list[dict[str, Any]]:
        return list(self._executed.values())
