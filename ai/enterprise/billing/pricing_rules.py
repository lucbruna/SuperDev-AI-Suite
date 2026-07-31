"""Pricing rules."""
from __future__ import annotations
from typing import Any, Callable, Dict, List

class PricingRules:
    def __init__(self) -> None:
        self._rules: List[Dict[str, Any]] = []
    def add_rule(self, name: str, condition: Callable[[Dict[str, Any]], bool], modifier: Callable[[float], float]) -> None:
        self._rules.append({"name": name, "condition": condition, "modifier": modifier})
    def apply_rules(self, base_price: float, context: Dict[str, Any]) -> float:
        price = base_price
        for rule in self._rules:
            if rule["condition"](context):
                price = rule["modifier"](price)
        return price
    def list_rules(self) -> List[str]:
        return [r["name"] for r in self._rules]
    def remove_rule(self, name: str) -> bool:
        before = len(self._rules)
        self._rules = [r for r in self._rules if r["name"] != name]
        return len(self._rules) < before
    def clear(self) -> int:
        n = len(self._rules)
        self._rules.clear()
        return n
