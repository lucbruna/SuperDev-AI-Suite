"""Payment history."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class PaymentHistory:
    def __init__(self) -> None:
        self._history: List[Dict[str, Any]] = []
    def record(self, payment_id: str, event: str, details: str = "", amount: float = 0.0) -> Dict[str, Any]:
        entry = {"payment_id": payment_id, "event": event, "details": details, "amount": amount, "timestamp": time.time()}
        self._history.append(entry)
        return entry
    def get_by_payment(self, payment_id: str) -> List[Dict[str, Any]]:
        return [h for h in self._history if h["payment_id"] == payment_id]
    def get_by_event(self, event: str, limit: int = 50) -> List[Dict[str, Any]]:
        return [h for h in self._history if h["event"] == event][-limit:]
    def list_recent(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self._history[-limit:]
    def count(self) -> int:
        return len(self._history)
    def clear(self) -> int:
        n = len(self._history)
        self._history.clear()
        return n
    def search(self, keyword: str, limit: int = 50) -> List[Dict[str, Any]]:
        return [h for h in self._history if keyword.lower() in str(h).lower()][-limit:]
