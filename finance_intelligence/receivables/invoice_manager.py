"""Invoice management for the Finance Intelligence Engine (Volume 35)."""

from __future__ import annotations

import time
from typing import Any

from finance_intelligence.finance_events import (FinanceEventType,
                                                 FinanceEvents)
from finance_intelligence.finance_metrics import FinanceMetrics
from finance_intelligence.finance_models import (Invoice, InvoiceStatus)
from finance_intelligence.finance_protocols import new_id, round_money


class InvoiceManager:
    """Issue, list and collect payments on invoices."""

    def __init__(self, events: FinanceEvents,
                 metrics: FinanceMetrics) -> None:
        self.events = events
        self.metrics = metrics
        self._invoices: dict[str, Invoice] = {}

    def issue(self, customer: str, amount: float,
              due_date: float = 0.0) -> Invoice:
        invoice = Invoice(
            invoice_id=new_id("invoice"), customer=customer,
            amount=round_money(amount), due_date=due_date,
            status=InvoiceStatus.ISSUED, issued_at=time.time())
        self._invoices[invoice.invoice_id] = invoice
        self.metrics.increment("fi.invoices.issued")
        self.events.publish(FinanceEventType.INVOICE_ISSUED,
                            {"invoice_id": invoice.invoice_id,
                             "customer": customer,
                             "amount": invoice.amount})
        return invoice

    def get(self, invoice_id: str) -> Invoice | None:
        return self._invoices.get(invoice_id)

    def list(self) -> list[Invoice]:
        return list(self._invoices.values())

    def register_payment(self, invoice_id: str,
                         amount: float) -> dict[str, Any]:
        invoice = self._invoices.get(invoice_id)
        if invoice is None:
            return {"invoice_id": invoice_id, "status": "not_found"}
        invoice.paid_amount = round_money(
            invoice.paid_amount + amount)
        if invoice.paid_amount >= invoice.amount:
            invoice.paid_amount = invoice.amount
            invoice.status = InvoiceStatus.PAID
            self.metrics.increment("fi.invoices.paid")
            self.events.publish(FinanceEventType.INVOICE_PAID,
                                {"invoice_id": invoice_id,
                                 "amount": invoice.amount})
        elif invoice.paid_amount > 0:
            invoice.status = InvoiceStatus.PARTIAL
        return {"invoice_id": invoice_id,
                "status": invoice.status.value,
                "outstanding": invoice.outstanding()}

    def mark_overdue(self) -> int:
        now = time.time()
        count = 0
        for invoice in self._invoices.values():
            if (invoice.status in (InvoiceStatus.ISSUED,
                                   InvoiceStatus.PARTIAL)
                    and invoice.due_date and invoice.due_date < now):
                invoice.status = InvoiceStatus.OVERDUE
                count += 1
        return count
