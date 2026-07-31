"""Receivables subsystem facade (Volume 35).

Aggregates invoice management, collection, customer debt and payment
prediction.
"""

from __future__ import annotations

from typing import Any

from finance_intelligence.finance_events import FinanceEvents
from finance_intelligence.finance_metrics import FinanceMetrics
from finance_intelligence.finance_registry import FinanceRegistry
from finance_intelligence.receivables.collection import Collection
from finance_intelligence.receivables.customer_debt import CustomerDebt
from finance_intelligence.receivables.invoice_manager import InvoiceManager
from finance_intelligence.receivables.payment_prediction import (
    PaymentPrediction)


class ReceivableEngine:
    """Aggregate facade over the receivables subsystems."""

    def __init__(self, registry: FinanceRegistry | None = None,
                 events: FinanceEvents | None = None,
                 metrics: FinanceMetrics | None = None) -> None:
        self.registry = registry or FinanceRegistry()
        self.events = events or FinanceEvents()
        self.metrics = metrics or FinanceMetrics()
        self.invoices = InvoiceManager(self.events, self.metrics)
        self.collection = Collection()
        self.debt = CustomerDebt()
        self.prediction = PaymentPrediction()

    # -- conveniences --------------------------------------------------------
    def issue_invoice(self, customer: str, amount: float,
                      due_date: float = 0.0):
        return self.invoices.issue(customer, amount, due_date)

    def record_payment(self, invoice_id: str, amount: float):
        return self.invoices.register_payment(invoice_id, amount)

    def outstanding_by_customer(self) -> dict[str, float]:
        return self.debt.outstanding_by_customer(self.invoices.list())

    def at_risk(self) -> list[dict[str, Any]]:
        return self.prediction.at_risk(self.invoices.list())

    def stats(self) -> dict[str, Any]:
        return {
            "invoices": len(self.invoices.list()),
            "outstanding": self.debt.total_outstanding(
                self.invoices.list()),
            "paid": self.metrics.count("fi.invoices.paid"),
            "issued": self.metrics.count("fi.invoices.issued"),
        }
