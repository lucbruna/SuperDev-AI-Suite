"""Transaction management."""

from __future__ import annotations

import time
import uuid
from typing import Any


class TransactionManager:
    def __init__(self) -> None:
        self._transactions: dict[str, dict[str, Any]] = {}

    def start_transaction(self, name: str, transaction_type: str = "request") -> str:
        tx_id = str(uuid.uuid4())[:8]
        self._transactions[tx_id] = {
            "id": tx_id,
            "name": name,
            "type": transaction_type,
            "start_time": time.time(),
            "spans": [],
            "status": "active",
        }
        return tx_id

    def end_transaction(self, tx_id: str, status: str = "success") -> dict[str, Any] | None:
        tx = self._transactions.get(tx_id)
        if not tx:
            return None
        tx["end_time"] = time.time()
        tx["duration_ms"] = (tx["end_time"] - tx["start_time"]) * 1000
        tx["status"] = status
        return tx

    def add_span_to_transaction(self, tx_id: str, span_id: str) -> bool:
        tx = self._transactions.get(tx_id)
        if tx:
            tx["spans"].append(span_id)
            return True
        return False

    def get_transaction(self, tx_id: str) -> dict[str, Any] | None:
        return self._transactions.get(tx_id)

    def list_transactions(self) -> list[dict[str, Any]]:
        return list(self._transactions.values())

    def get_slow_transactions(self, threshold_ms: float = 1000) -> list[dict[str, Any]]:
        return [t for t in self._transactions.values() if t.get("duration_ms", 0) > threshold_ms]
