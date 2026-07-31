"""Collections for the Finance Intelligence Engine (Volume 35)."""

from __future__ import annotations

import time
from typing import Any

from finance_intelligence.finance_models import Invoice, InvoiceStatus


class Collection:
    """Track collection attempts on overdue receivables."""

    def __init__(self) -> None:
        self._attempts: list[dict[str, Any]] = []

    def record_attempt(self, invoice: Invoice, channel: str,
                       result: str, note: str = "") -> dict[str, Any]:
        attempt = {
            "invoice_id": invoice.invoice_id,
            "customer": invoice.customer,
            "channel": channel,
            "result": result,
            "note": note,
            "at": time.time(),
        }
        self._attempts.append(attempt)
        return attempt

    def list_attempts(self) -> list[dict[str, Any]]:
        return list(self._attempts)

    def attempts_for(self, invoice_id: str) -> list[dict[str, Any]]:
        return [attempt for attempt in self._attempts
                if attempt["invoice_id"] == invoice_id]

    def status_overview(self, invoices: list[Invoice]) -> dict[str, int]:
        overview: dict[str, int] = {}
        for invoice in invoices:
            overview[invoice.status.value] = (
                overview.get(invoice.status.value, 0) + 1)
        return overview

    def overdue_list(self, invoices: list[Invoice]) -> list[Invoice]:
        now = time.time()
        return [invoice for invoice in invoices
                if invoice.status in (InvoiceStatus.ISSUED,
                                      InvoiceStatus.PARTIAL)
                and invoice.due_date and invoice.due_date < now]
