"""Payment refunds."""

from __future__ import annotations

import time
from typing import Any


class RefundManager:
    def __init__(self) -> None:
        self._refunds: list[dict[str, Any]] = []

    def refund(self, payment_id: str, amount: float, reason: str = "") -> dict[str, Any]:
        import uuid

        refund = {
            "id": str(uuid.uuid4())[:8],
            "payment_id": payment_id,
            "amount": amount,
            "reason": reason,
            "status": "pending",
            "created_at": time.time(),
        }
        self._refunds.append(refund)
        return refund

    def process(self, refund_id: str) -> bool:
        for r in self._refunds:
            if r["id"] == refund_id:
                r["status"] = "processed"
                r["processed_at"] = time.time()
                return True
        return False

    def reject(self, refund_id: str) -> bool:
        for r in self._refunds:
            if r["id"] == refund_id:
                r["status"] = "rejected"
                return True
        return False

    def get(self, refund_id: str) -> dict[str, Any]:
        for r in self._refunds:
            if r["id"] == refund_id:
                return r
        return {}

    def list_by_payment(self, payment_id: str) -> list[dict[str, Any]]:
        return [r for r in self._refunds if r["payment_id"] == payment_id]

    def list_all(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._refunds[-limit:]

    def total_refunded(self) -> float:
        return sum(r["amount"] for r in self._refunds if r["status"] == "processed")

    def count(self) -> int:
        return len(self._refunds)
