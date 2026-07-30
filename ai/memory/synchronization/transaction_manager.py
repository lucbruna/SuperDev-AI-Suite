from __future__ import annotations

import time
from typing import Any, Dict, List, Optional


class Transaction:
    """A single sync transaction."""

    def __init__(self, transaction_id: str, operations: List[Dict[str, Any]]):
        self._transaction_id = transaction_id
        self._operations = list(operations)
        self._status: str = "pending"
        self._created_at = time.time()
        self._completed_at: Optional[float] = None

    @property
    def transaction_id(self) -> str:
        return self._transaction_id

    @property
    def operations(self) -> List[Dict[str, Any]]:
        return list(self._operations)

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, value: str) -> None:
        self._status = value
        if value in ("committed", "rolled_back"):
            self._completed_at = time.time()

    @property
    def created_at(self) -> float:
        return self._created_at

    @property
    def completed_at(self) -> Optional[float]:
        return self._completed_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transaction_id": self._transaction_id,
            "operations": list(self._operations),
            "status": self._status,
            "created_at": self._created_at,
            "completed_at": self._completed_at,
        }


class TransactionManager:
    """Manages transactions for safe memory synchronization."""

    def __init__(self):
        self._transactions: Dict[str, Transaction] = {}
        self._counter: int = 0

    @property
    def active_count(self) -> int:
        return sum(1 for t in self._transactions.values() if t.status == "pending")

    def begin(self, operations: List[Dict[str, Any]]) -> Transaction:
        self._counter += 1
        tx = Transaction(f"tx_{self._counter}", operations)
        self._transactions[tx.transaction_id] = tx
        return tx

    def commit(self, tx_id: str) -> bool:
        tx = self._transactions.get(tx_id)
        if tx is None or tx.status != "pending":
            return False
        tx.status = "committed"
        return True

    def rollback(self, tx_id: str) -> bool:
        tx = self._transactions.get(tx_id)
        if tx is None or tx.status != "pending":
            return False
        tx.status = "rolled_back"
        return True

    def get_transaction(self, tx_id: str) -> Optional[Transaction]:
        return self._transactions.get(tx_id)

    def list_active(self) -> List[Transaction]:
        return [t for t in self._transactions.values() if t.status == "pending"]

    def list_all(self) -> List[Transaction]:
        return list(self._transactions.values())

    def clear(self) -> None:
        self._transactions.clear()
