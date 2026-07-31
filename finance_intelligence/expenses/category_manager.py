"""Expense category management for the Finance Intelligence Engine (V35)."""

from __future__ import annotations

from typing import Any

from finance_intelligence.finance_protocols import new_id, round_money


class CategoryManager:
    """Define expense categories and classify expenses."""

    _DEFAULTS = ["Operacional", "Pessoal", "Marketing", "Tecnologia",
                 "Fornecedores", "Impostos", "Outros"]

    def __init__(self) -> None:
        self._categories: dict[str, dict[str, Any]] = {}
        for name in self._DEFAULTS:
            self.add(name)

    def add(self, name: str, description: str = "",
            budget: float = 0.0) -> dict[str, Any]:
        category = {"category_id": new_id("category"), "name": name,
                    "description": description, "budget": budget}
        self._categories[category["category_id"]] = category
        return category

    def list(self) -> list[dict[str, Any]]:
        return list(self._categories.values())

    def get(self, category_id: str) -> dict[str, Any] | None:
        return self._categories.get(category_id)

    def find_by_name(self, name: str) -> dict[str, Any] | None:
        for category in self._categories.values():
            if category["name"].lower() == name.lower():
                return category
        return None

    def classify(self, description: str) -> str:
        """Best-effort category by keyword in the description."""
        description_lower = (description or "").lower()
        for category in self._categories.values():
            if category["name"].lower() in description_lower:
                return category["category_id"]
        fallback = self.find_by_name("Outros")
        return fallback["category_id"] if fallback else ""

    def spending_by_category(
            self, expenses: list[Any]) -> dict[str, float]:
        totals: dict[str, float] = {}
        for expense in expenses:
            meta = getattr(expense, "metadata", None) or {}
            category_id = meta.get("category_id", "") or \
                getattr(expense, "category_id", "")
            totals[category_id] = round_money(
                totals.get(category_id, 0.0) + expense.amount)
        return totals
