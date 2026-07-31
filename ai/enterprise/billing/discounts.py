"""Discount management."""
from __future__ import annotations
from typing import Any, Dict, List

class DiscountManager:
    def __init__(self) -> None:
        self._discounts: Dict[str, Dict[str, Any]] = {}
    def add(self, code: str, percent: float, description: str = "", max_uses: int = 0, valid_until: float = 0) -> Dict[str, Any]:
        discount = {"code": code, "percent": percent, "description": description, "max_uses": max_uses, "used": 0, "valid_until": valid_until, "active": True}
        self._discounts[code] = discount
        return discount
    def get(self, code: str) -> Dict[str, Any]:
        return self._discounts.get(code, {})
    def apply(self, code: str, amount: float) -> float:
        discount = self._discounts.get(code)
        if not discount or not discount["active"]:
            return 0.0
        if discount["max_uses"] > 0 and discount["used"] >= discount["max_uses"]:
            return 0.0
        discount["used"] += 1
        return amount * (discount["percent"] / 100)
    def deactivate(self, code: str) -> bool:
        if code in self._discounts:
            self._discounts[code]["active"] = False
            return True
        return False
    def list_active(self) -> List[Dict[str, Any]]:
        return [d for d in self._discounts.values() if d["active"]]
    def remove(self, code: str) -> bool:
        if code in self._discounts:
            del self._discounts[code]
            return True
        return False
