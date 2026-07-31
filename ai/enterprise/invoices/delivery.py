"""Invoice delivery."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class InvoiceDelivery:
    def __init__(self) -> None:
        self._deliveries: List[Dict[str, Any]] = []
    def deliver(self, invoice_id: str, method: str, recipient: str) -> Dict[str, Any]:
        entry = {"invoice_id": invoice_id, "method": method, "recipient": recipient, "status": "sent", "delivered_at": time.time()}
        self._deliveries.append(entry)
        return entry
    def mark_read(self, invoice_id: str) -> bool:
        for d in self._deliveries:
            if d["invoice_id"] == invoice_id:
                d["status"] = "read"
                d["read_at"] = time.time()
                return True
        return False
    def list_deliveries(self, invoice_id: str = "", limit: int = 50) -> List[Dict[str, Any]]:
        results = self._deliveries
        if invoice_id:
            results = [d for d in results if d["invoice_id"] == invoice_id]
        return results[-limit:]
    def count(self) -> int:
        return len(self._deliveries)
    def get_status(self, invoice_id: str) -> str:
        for d in self._deliveries:
            if d["invoice_id"] == invoice_id:
                return d["status"]
        return "not_sent"
