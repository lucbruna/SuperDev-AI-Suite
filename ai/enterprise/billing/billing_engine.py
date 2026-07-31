"""Billing engine."""

from __future__ import annotations

import time
from typing import Any


class BillingEngine:
    def __init__(self) -> None:
        self._charges: list[dict[str, Any]] = []
        self._started = False

    def start(self) -> None:
        self._started = True

    def charge(
        self, org_id: str, amount: float, description: str = "", metadata: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        import uuid

        charge = {
            "id": str(uuid.uuid4())[:8],
            "org_id": org_id,
            "amount": amount,
            "description": description,
            "metadata": metadata or {},
            "status": "pending",
            "created_at": time.time(),
        }
        self._charges.append(charge)
        return charge

    def list_charges(self, org_id: str = "", limit: int = 50) -> list[dict[str, Any]]:
        results = self._charges
        if org_id:
            results = [c for c in results if c["org_id"] == org_id]
        return results[-limit:]

    def total_charges(self, org_id: str = "") -> float:
        results = self._charges
        if org_id:
            results = [c for c in results if c["org_id"] == org_id]
        return sum(c["amount"] for c in results)

    def is_running(self) -> bool:
        return self._started
