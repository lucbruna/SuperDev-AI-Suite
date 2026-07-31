"""Recommendation engine for the Finance Intelligence Engine (V35)."""

from __future__ import annotations

from typing import Any

_ACTIONS = {
    "negative_net_position": {
        "action": "increase_revenue_focus",
        "priority": "high",
        "reason": "reduce the gap between revenue and expenses",
    },
    "expense_concentration": {
        "action": "diversify_spending",
        "priority": "medium",
        "reason": "reduce reliance on a single expense category",
    },
    "open_alert": {
        "action": "review_risk_alerts",
        "priority": "high",
        "reason": "unresolved high-severity alerts need attention",
    },
    "budget_overrun": {
        "action": "reduce_spending",
        "priority": "medium",
        "reason": "control categories that exceed their budgets",
    },
}


class RecommendationEngine:
    """Map insights to actionable recommendations."""

    def recommend(self, insights: list[dict[str, Any]]
                  ) -> list[dict[str, Any]]:
        seen: set[str] = set()
        recommendations: list[dict[str, Any]] = []
        for insight in insights:
            template = _ACTIONS.get(insight["type"])
            if template is None or template["action"] in seen:
                continue
            seen.add(template["action"])
            recommendations.append({
                "action": template["action"],
                "priority": template["priority"],
                "reason": template["reason"],
                "source": insight["type"],
            })
        return recommendations

    def prioritize(self, recommendations: list[dict[str, Any]]
                   ) -> list[dict[str, Any]]:
        rank = {"high": 0, "medium": 1, "low": 2}
        return sorted(recommendations,
                      key=lambda rec: rank.get(rec["priority"], 3))
