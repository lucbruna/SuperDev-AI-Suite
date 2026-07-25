from __future__ import annotations as __

import asyncio
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import uuid4
from dataclasses import dataclass, field

from pydantic import BaseModel, Field


class InvoiceItem(BaseModel):
    description: str
    quantity: int = 1
    unit_price: float
    amount: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Invoice(BaseModel):
    id: str = Field(default_factory=lambda: f"inv_{uuid4().hex[:12]}")
    org_id: str
    subscription_id: str
    amount: float = 0.0
    currency: str = "USD"
    status: str = Field(default="pending", pattern=r"^(pending|paid|overdue|canceled|refunded)$")
    items: List[InvoiceItem] = Field(default_factory=list)
    period_start: datetime
    period_end: datetime
    due_date: datetime
    paid_at: datetime | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    notes: str = ""


class InvoiceManager:
    _invoices: Dict[str, Invoice] = {}

    async def generate_invoice(
        self, subscription_id: str, period: tuple[datetime, datetime], org_id: str = ""
    ) -> Invoice:
        await asyncio.sleep(0.01)
        period_start, period_end = period
        invoice = Invoice(
            org_id=org_id,
            subscription_id=subscription_id,
            period_start=period_start,
            period_end=period_end,
            due_date=period_end + timedelta(days=30),
        )
        self._invoices[invoice.id] = invoice
        return invoice

    async def list_invoices(self, org_id: str) -> List[Invoice]:
        await asyncio.sleep(0.01)
        return [inv for inv in self._invoices.values() if inv.org_id == org_id]

    async def get_invoice(self, invoice_id: str) -> Invoice | None:
        await asyncio.sleep(0.01)
        return self._invoices.get(invoice_id)

    async def send_invoice(self, invoice_id: str, email: str) -> bool:
        await asyncio.sleep(0.05)
        invoice = self._invoices.get(invoice_id)
        if not invoice:
            return False
        invoice.status = "pending"
        return True

    async def mark_paid(self, invoice_id: str) -> bool:
        invoice = self._invoices.get(invoice_id)
        if not invoice:
            return False
        invoice.status = "paid"
        invoice.paid_at = datetime.utcnow()
        return True
