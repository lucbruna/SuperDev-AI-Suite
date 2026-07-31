"""Invoice calculation."""
from __future__ import annotations
from typing import Any, Dict, List

class InvoiceCalculator:
    def __init__(self, tax_rate: float = 0.0, discount: float = 0.0) -> None:
        self._tax_rate = tax_rate
        self._discount = discount
    def calculate(self, items: List[Dict[str, Any]]) -> Dict[str, float]:
        subtotal = sum(item.get("amount", 0) * item.get("quantity", 1) for item in items)
        discount = subtotal * (self._discount / 100)
        taxable = subtotal - discount
        tax = taxable * (self._tax_rate / 100)
        total = taxable + tax
        return {"subtotal": subtotal, "discount": discount, "tax": tax, "total": total}
    def add_item(self, description: str, amount: float, quantity: int = 1) -> Dict[str, Any]:
        return {"description": description, "amount": amount, "quantity": quantity, "total": amount * quantity}
    def set_tax_rate(self, rate: float) -> None:
        self._tax_rate = rate
    def set_discount(self, discount: float) -> None:
        self._discount = discount
    def calculate_line_total(self, amount: float, quantity: int) -> float:
        return amount * quantity
