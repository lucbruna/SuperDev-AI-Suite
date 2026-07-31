from __future__ import annotations

import logging
import time
from typing import Any

from ...frontend_context import FrontendContext


class BillingEngine:
    """Renders the billing page."""

    def __init__(self, context: FrontendContext | None = None) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.billing")
        self._context = context or FrontendContext()
        self._invoices: list[dict[str, Any]] = []

    def render(self, **kwargs: Any) -> dict[str, Any]:
        return {
            "page": "billing",
            "plan": self.plan(),
            "invoices": list(self._invoices),
        }

    def plan(self) -> dict[str, Any]:
        return {
            "name": "Enterprise",
            "seats": 25,
            "price_per_seat": 79.0,
            "billing_cycle": "monthly",
            "status": "active",
        }

    def add_invoice(self, amount: float, description: str, status: str = "paid") -> str:
        invoice_id = f"inv-{len(self._invoices) + 1}"
        self._invoices.append(
            {"invoice_id": invoice_id, "amount": amount, "description": description, "status": status, "issued_at": time.time()}
        )
        return invoice_id
