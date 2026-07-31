"""Tax management."""
from __future__ import annotations
from typing import Any, Dict, List

class TaxManager:
    def __init__(self) -> None:
        self._taxes: Dict[str, Dict[str, Any]] = {}
    def add_tax(self, name: str, rate: float, description: str = "", applies_to: str = "all") -> Dict[str, Any]:
        tax = {"name": name, "rate": rate, "description": description, "applies_to": applies_to, "active": True}
        self._taxes[name] = tax
        return tax
    def get_tax(self, name: str) -> Dict[str, Any]:
        return self._taxes.get(name, {})
    def calculate_tax(self, amount: float, tax_name: str = "") -> float:
        if tax_name:
            tax = self._taxes.get(tax_name, {})
            return amount * (tax.get("rate", 0) / 100)
        total_tax = 0.0
        for tax in self._taxes.values():
            if tax["active"]:
                total_tax += amount * (tax["rate"] / 100)
        return total_tax
    def list_taxes(self) -> List[Dict[str, Any]]:
        return list(self._taxes.values())
    def deactivate(self, name: str) -> bool:
        if name in self._taxes:
            self._taxes[name]["active"] = False
            return True
        return False
    def remove(self, name: str) -> bool:
        if name in self._taxes:
            del self._taxes[name]
            return True
        return False
