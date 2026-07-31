"""Revenue analytics."""

from __future__ import annotations

from typing import Any


class RevenueAnalytics:
    def __init__(self) -> None:
        self._revenue: dict[str, float] = {}
        self._breakdown: dict[str, dict[str, float]] = {}

    def record(self, org_id: str, amount: float, category: str = "subscription") -> None:
        self._revenue[org_id] = self._revenue.get(org_id, 0) + amount
        self._breakdown.setdefault(org_id, {})
        self._breakdown[org_id][category] = self._breakdown[org_id].get(category, 0) + amount

    def total_revenue(self) -> float:
        return sum(self._revenue.values())

    def revenue_by_org(self, org_id: str) -> float:
        return self._revenue.get(org_id, 0.0)

    def breakdown_by_org(self, org_id: str) -> dict[str, float]:
        return dict(self._breakdown.get(org_id, {}))

    def top_customers(self, limit: int = 10) -> list[dict[str, Any]]:
        sorted_revs = sorted(self._revenue.items(), key=lambda x: x[1], reverse=True)[:limit]
        return [{"org_id": org, "revenue": rev} for org, rev in sorted_revs]

    def total_by_category(self) -> dict[str, float]:
        totals: dict[str, float] = {}
        for breakdown in self._breakdown.values():
            for cat, amt in breakdown.items():
                totals[cat] = totals.get(cat, 0) + amt
        return totals

    def list_orgs(self) -> list[str]:
        return list(self._revenue.keys())

    def clear(self) -> float:
        old = self.total_revenue()
        self._revenue.clear()
        self._breakdown.clear()
        return old
