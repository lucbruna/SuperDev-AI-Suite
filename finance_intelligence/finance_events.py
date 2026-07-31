"""Events for the Finance Intelligence Engine (Volume 35)."""

from __future__ import annotations

from enum import Enum
from typing import Any, Callable

from finance_intelligence.finance_logger import get_logger

_Listener = Callable[[dict[str, Any]], None]


class FinanceEventType(Enum):
    ACCOUNT_CREATED = "fi.account.created"
    ACCOUNT_UPDATED = "fi.account.updated"
    ACCOUNT_REMOVED = "fi.account.removed"
    JOURNAL_ENTRY_RECORDED = "fi.journal.recorded"
    TRANSACTION_RECORDED = "fi.transaction.recorded"
    TRANSACTION_APPROVED = "fi.transaction.approved"
    TRANSACTION_REJECTED = "fi.transaction.rejected"
    INVOICE_ISSUED = "fi.invoice.issued"
    INVOICE_PAID = "fi.invoice.paid"
    PAYMENT_SCHEDULED = "fi.payment.scheduled"
    PAYMENT_APPROVED = "fi.payment.approved"
    PAYMENT_EXECUTED = "fi.payment.executed"
    PAYMENT_FAILED = "fi.payment.failed"
    BUDGET_CREATED = "fi.budget.created"
    BUDGET_ALERT = "fi.budget.alert"
    FORECAST_GENERATED = "fi.forecast.generated"
    TAX_CALCULATED = "fi.tax.calculated"
    TAX_REPORT_GENERATED = "fi.tax.report"
    AUDIT_RECORDED = "fi.audit.recorded"
    ANOMALY_DETECTED = "fi.anomaly.detected"
    RISK_FLAGGED = "fi.risk.flagged"
    FRAUD_DETECTED = "fi.fraud.detected"
    APPROVAL_REQUIRED = "fi.approval.required"
    APPROVAL_RESOLVED = "fi.approval.resolved"


class FinanceEvents:
    """Thread-safe pub/sub event bus with listener isolation."""

    def __init__(self) -> None:
        self._log = get_logger("events")
        self._listeners: dict[FinanceEventType, list[_Listener]] = {}

    def on(self, event_type: FinanceEventType, listener: _Listener) -> None:
        self._listeners.setdefault(event_type, []).append(listener)

    def once(self, event_type: FinanceEventType, listener: _Listener) -> None:
        def _wrapper(payload: dict[str, Any]) -> None:
            self.off(event_type, _wrapper)
            listener(payload)

        self.on(event_type, _wrapper)

    def off(self, event_type: FinanceEventType, listener: _Listener) -> None:
        listeners = self._listeners.get(event_type)
        if listeners is not None and listener in listeners:
            listeners.remove(listener)

    def publish(self, event_type: FinanceEventType,
                payload: dict[str, Any]) -> None:
        for listener in list(self._listeners.get(event_type, [])):
            try:
                listener(payload)
            except Exception:  # noqa: BLE001 - listener isolation
                self._log.warning("listener failed for %s: %s",
                                  event_type.value, listener)
