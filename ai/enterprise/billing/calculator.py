"""Billing calculator."""
from __future__ import annotations
from typing import Any, Dict, List

class BillingCalculator:
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
    def set_tax_rate(self, rate: float) -> None:
        self._tax_rate = rate
    def set_discount(self, discount: float) -> None:
        self._discount = discount
    def get_tax_rate(self) -> float:
        return self._tax_rate
    def get_discount(self) -> float:
        return self._discount
    def calculate_prorated(self, full_price: float, days_used: int, total_days: int) -> float:
        if total_days == 0:
            return 0.0
        return full_price * (days_used / total_days)
