"""Cost optimization for the Finance Intelligence Engine (Volume 35)."""

from __future__ import annotations

from typing import Any

from finance_intelligence.finance_protocols import round_money, top_n


class CostOptimizer:
    """Suggest expense reduction opportunities."""

    def suggestions(self, expenses: list[Any],
                    categories: dict[str, dict[str, Any]],
                    reduction_rate: float = 0.1) -> list[dict[str, Any]]:
        """Top categories by spend, each with a target reduction."""
        totals: dict[str, float] = {}
        counts: dict[str, int] = {}
        for expense in expenses:
            meta = getattr(expense, "metadata", None) or {}
            category_id = meta.get("category_id", "") or \
                getattr(expense, "category_id", "")
            totals[category_id] = round_money(
                totals.get(category_id, 0.0) + expense.amount)
            counts[category_id] = counts.get(category_id, 0) + 1
        ranked = sorted(totals.items(), key=lambda item: item[1],
                        reverse=True)
        suggestions = []
        for category_id, total in ranked:
            name = categories.get(category_id, {}).get("name", category_id)
            suggestions.append({
                "category": name,
                "category_id": category_id,
                "total": total,
                "transactions": counts.get(category_id, 0),
                "potential_saving": round_money(total * reduction_rate),
                "rate": reduction_rate,
            })
        return suggestions

    def top_savings(self, expenses: list[Any],
                    categories: dict[str, dict[str, Any]],
                    limit: int = 3) -> list[dict[str, Any]]:
        suggestions = self.suggestions(expenses, categories)
        return top_n(suggestions, key=lambda item: item["potential_saving"],
                     limit=limit)

    def recurring_estimate(self, expenses: list[Any],
                           periods: int = 12) -> dict[str, Any]:
        """Project annual spend based on current average period spend."""
        total = round_money(sum(expense.amount for expense in expenses))
        if not expenses:
            return {"total": 0.0, "annual_projection": 0.0,
                    "average": 0.0}
        average = round_money(total / len(expenses))
        return {
            "total": total,
            "transaction_count": len(expenses),
            "average": average,
            "annual_projection": round_money(average * periods),
        }
