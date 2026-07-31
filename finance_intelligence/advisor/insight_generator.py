"""Insight generation for the Finance Intelligence Engine (Volume 35)."""

from __future__ import annotations

from typing import Any

from finance_intelligence.finance_models import (FinancialAlert, RiskLevel,
                                                 Transaction,
                                                 TransactionType)
from finance_intelligence.finance_protocols import round_money


class InsightGenerator:
    """Derive financial insights from transactions, budgets and alerts."""

    def generate(self, transactions: list[Transaction],
                 budgets: list[Any] | None = None,
                 alerts: list[FinancialAlert] | None = None
                 ) -> list[dict[str, Any]]:
        insights: list[dict[str, Any]] = []
        revenue = sum(tx.amount for tx in transactions
                      if tx.kind in (TransactionType.REVENUE,
                                     TransactionType.RECEIPT))
        expenses = sum(tx.amount for tx in transactions
                       if tx.kind in (TransactionType.EXPENSE,
                                      TransactionType.PAYMENT))
        net = round_money(revenue - expenses)
        if net < 0:
            insights.append({
                "type": "negative_net_position",
                "severity": "high",
                "message": "expenses exceed revenue for the period",
                "metric": net,
            })
        elif transactions:
            insights.append({
                "type": "positive_net_position",
                "severity": "low",
                "message": "revenue exceeds expenses for the period",
                "metric": net,
            })

        total = revenue + expenses
        by_category: dict[str, float] = {}
        for tx in transactions:
            if tx.kind not in (TransactionType.EXPENSE,
                               TransactionType.PAYMENT):
                continue
            meta = getattr(tx, "metadata", None) or {}
            category = meta.get("category_id", "") or "uncategorized"
            by_category[category] = round_money(
                by_category.get(category, 0.0) + tx.amount)
        if by_category:
            top_category, top_amount = max(
                by_category.items(), key=lambda item: item[1])
            share = top_amount / total if total else 0.0
            if share >= 0.5:
                insights.append({
                    "type": "expense_concentration",
                    "severity": "medium",
                    "message": f"category {top_category!r} is {share:.0%} "
                               "of all spending",
                    "metric": round_money(share),
                })

        for alert in (alerts or []):
            if not alert.resolved and alert.level in (
                    RiskLevel.HIGH, RiskLevel.CRITICAL):
                insights.append({
                    "type": "open_alert",
                    "severity": "high",
                    "message": alert.message or "unresolved risk alert",
                    "metric": alert.level.value,
                })

        for budget in (budgets or []):
            if getattr(budget, "actual", 0.0) > getattr(
                    budget, "planned", 0.0):
                insights.append({
                    "type": "budget_overrun",
                    "severity": "medium",
                    "message": f"budget {getattr(budget, 'category', '')} "
                               "is over its plan",
                    "metric": round_money(getattr(budget, "variance", lambda: 0.0)()),
                })

        return insights
