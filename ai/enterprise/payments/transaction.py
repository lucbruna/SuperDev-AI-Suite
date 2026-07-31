"""Payment transactions."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class TransactionManager:
    def __init__(self) -> None:
        self._transactions: List[Dict[str, Any]] = []
    def create(self, payment_id: str, amount: float, method: str, gateway: str = "") -> Dict[str, Any]:
        import uuid
        tx = {"id": str(uuid.uuid4())[:8], "payment_id": payment_id, "amount": amount, "method": method, "gateway": gateway, "status": "initiated", "created_at": time.time()}
        self._transactions.append(tx)
        return tx
    def update_status(self, tx_id: str, status: str) -> bool:
        for tx in self._transactions:
            if tx["id"] == tx_id:
                tx["status"] = status
                tx["updated_at"] = time.time()
                return True
        return False
    def get(self, tx_id: str) -> Dict[str, Any]:
        for tx in self._transactions:
            if tx["id"] == tx_id:
                return tx
        return {}
    def list_by_payment(self, payment_id: str) -> List[Dict[str, Any]]:
        return [tx for tx in self._transactions if tx["payment_id"] == payment_id]
    def list_recent(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._transactions[-limit:]
    def count(self) -> int:
        return len(self._transactions)
    def total_amount(self) -> float:
        return sum(tx["amount"] for tx in self._transactions if tx["status"] == "completed")
