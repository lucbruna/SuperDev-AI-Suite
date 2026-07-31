"""Plan pricing."""
from __future__ import annotations

from typing import Any


class PricingManager:
    def __init__(self) -> None:
        self._pricing: dict[str, dict[str, Any]] = {}
    def set_price(self, plan_id: str, amount: float, currency: str = "BRL", cycle: str = "monthly") -> dict[str, Any]:
        price = {"plan_id": plan_id, "amount": amount, "currency": currency, "cycle": cycle}
        self._pricing[plan_id] = price
        return price
    def get_price(self, plan_id: str) -> dict[str, Any]:
        return self._pricing.get(plan_id, {"amount": 0, "currency": "BRL"})
    def calculate_annual(self, plan_id: str) -> float:
        price = self.get_price(plan_id)
        monthly = price.get("amount", 0)
        return monthly * 12
    def apply_discount(self, plan_id: str, discount_percent: float) -> float:
        price = self.get_price(plan_id)
        original = price.get("amount", 0)
        return original * (1 - discount_percent / 100)
    def list_all(self) -> dict[str, dict[str, Any]]:
        return dict(self._pricing)
    def remove(self, plan_id: str) -> bool:
        if plan_id in self._pricing:
            del self._pricing[plan_id]
            return True
        return False
