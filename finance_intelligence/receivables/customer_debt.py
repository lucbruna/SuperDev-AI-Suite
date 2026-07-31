"""Customer debt aggregation for the Finance Intelligence Engine (V35)."""

from __future__ import annotations

from typing import Any

from finance_intelligence.finance_models import (Invoice, InvoiceStatus)
from finance_intelligence.finance_protocols import round_money


class CustomerDebt:
    """Aggregate outstanding balances by customer."""

    def __init__(self) -> None:
        self._customers: dict[str, dict[str, Any]] = {}

    def outstanding_by_customer(
            self, invoices: list[Invoice]) -> dict[str, float]:
        balances: dict[str, float] = {}
        for invoice in invoices:
            if invoice.status in (InvoiceStatus.CANCELLED,):
                continue
            outstanding = invoice.outstanding()
            if outstanding <= 0:
                continue
            balances[invoice.customer] = round_money(
                balances.get(invoice.customer, 0.0) + outstanding)
        return balances

    def total_outstanding(self, invoices: list[Invoice]) -> float:
        return round_money(
            sum(self.outstanding_by_customer(invoices).values()))

    def top_debtors(self, invoices: list[Invoice],
                    limit: int = 5) -> list[dict[str, Any]]:
        balances = self.outstanding_by_customer(invoices)
        ranked = sorted(balances.items(), key=lambda item: item[1],
                        reverse=True)[:max(0, limit)]
        return [{"customer": customer, "outstanding": amount}
                for customer, amount in ranked]

    def customer_summary(self, customer: str,
                         invoices: list[Invoice]) -> dict[str, Any]:
        customer_invoices = [invoice for invoice in invoices
                             if invoice.customer == customer]
        open_invoices = [invoice for invoice in customer_invoices
                         if invoice.outstanding() > 0]
        return {
            "customer": customer,
            "total_invoices": len(customer_invoices),
            "open_invoices": len(open_invoices),
            "outstanding": self.total_outstanding(customer_invoices),
        }
