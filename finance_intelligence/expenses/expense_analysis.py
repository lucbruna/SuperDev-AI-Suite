"""Expense analysis for the Finance Intelligence Engine (Volume 35)."""

from __future__ import annotations

from typing import Any

from finance_intelligence.finance_protocols import round_money, top_n


class ExpenseAnalysis:
    """Aggregate expense trends and top spenders."""

    def monthly_totals(self, expenses: list[Any]) -> dict[str, float]:
        totals: dict[str, float] = {}
        for expense in expenses:
            meta = getattr(expense, "metadata", None) or {}
            month = meta.get("month", "") or getattr(expense, "month", "")
            if not month:
                continue
            totals[month] = round_money(
                totals.get(month, 0.0) + expense.amount)
        return totals

    def by_category(self, expenses: list[Any],
                    categories: dict[str, dict[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for expense in expenses:
            meta = getattr(expense, "metadata", None) or {}
            category_id = meta.get("category_id", "") or \
                getattr(expense, "category_id", "")
            name = categories.get(category_id, {}).get("name", category_id)
            bucket = result.setdefault(name, {"count": 0, "total": 0.0})
            bucket["count"] += 1
            bucket["total"] = round_money(bucket["total"] + expense.amount)
        return result

    def top_expenses(self, expenses: list[Any],
                     limit: int = 5) -> list[Any]:
        return top_n(expenses, key=lambda expense: expense.amount,
                     limit=limit)

    def average_per_category(self, expenses: list[Any],
                             categories: dict[str, dict[str, Any]],
                             ) -> dict[str, float]:
        by_category = self.by_category(expenses, categories)
        return {name: round_money(bucket["total"] / bucket["count"])
                for name, bucket in by_category.items()}
