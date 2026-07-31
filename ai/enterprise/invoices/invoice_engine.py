"""Invoice engine."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time

class InvoiceEngine:
    def __init__(self) -> None:
        self._invoices: Dict[str, Dict[str, Any]] = {}
        self._counter = 0
        self._started = False
    def start(self) -> None:
        self._started = True
    def create(self, org_id: str, items: List[Dict[str, Any]], tax_rate: float = 0.0) -> Dict[str, Any]:
        import uuid
        self._counter += 1
        invoice_id = str(uuid.uuid4())[:8]
        subtotal = sum(item.get("amount", 0) * item.get("quantity", 1) for item in items)
        tax = subtotal * (tax_rate / 100)
        total = subtotal + tax
        invoice = {"id": invoice_id, "number": f"INV-{self._counter:06d}", "org_id": org_id, "items": items, "subtotal": subtotal, "tax": tax, "total": total, "status": "draft", "created_at": time.time()}
        self._invoices[invoice_id] = invoice
        return invoice
    def get(self, invoice_id: str) -> Optional[Dict[str, Any]]:
        return self._invoices.get(invoice_id)
    def send(self, invoice_id: str) -> bool:
        inv = self._invoices.get(invoice_id)
        if inv:
            inv["status"] = "sent"
            inv["sent_at"] = time.time()
            return True
        return False
    def pay(self, invoice_id: str) -> bool:
        inv = self._invoices.get(invoice_id)
        if inv:
            inv["status"] = "paid"
            inv["paid_at"] = time.time()
            return True
        return False
    def void(self, invoice_id: str) -> bool:
        inv = self._invoices.get(invoice_id)
        if inv:
            inv["status"] = "void"
            return True
        return False
    def list_by_org(self, org_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        return [i for i in self._invoices.values() if i["org_id"] == org_id][-limit:]
    def list_all(self, limit: int = 100) -> List[Dict[str, Any]]:
        return list(self._invoices.values())[-limit:]
    def count(self) -> int:
        return len(self._invoices)
    def is_running(self) -> bool:
        return self._started
