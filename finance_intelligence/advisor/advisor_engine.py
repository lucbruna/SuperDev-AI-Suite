"""AI advisor subsystem facade (Volume 35).

Aggregates insight generation and recommendations into a finance advisory
report.
"""

from __future__ import annotations

from typing import Any

from finance_intelligence.advisor.insight_generator import InsightGenerator
from finance_intelligence.advisor.recommendation_engine import (
    RecommendationEngine)
from finance_intelligence.finance_events import (FinanceEventType,
                                                 FinanceEvents)
from finance_intelligence.finance_metrics import FinanceMetrics
from finance_intelligence.finance_registry import FinanceRegistry


class AdvisorEngine:
    """Aggregate facade over the advisory subsystems."""

    def __init__(self, registry: FinanceRegistry | None = None,
                 events: FinanceEvents | None = None,
                 metrics: FinanceMetrics | None = None,
                 budget_engine: Any | None = None) -> None:
        self.registry = registry or FinanceRegistry()
        self.events = events or FinanceEvents()
        self.metrics = metrics or FinanceMetrics()
        self.budget_engine = budget_engine
        self.generator = InsightGenerator()
        self.recommender = RecommendationEngine()

    # -- advisory ------------------------------------------------------------
    def insights(self) -> list[dict[str, Any]]:
        budgets = []
        if self.budget_engine is not None:
            budgets = self.budget_engine.manager.list()
        return self.generator.generate(
            self.registry.list_transactions(),
            budgets=budgets,
            alerts=self.registry.list_alerts())

    def report(self) -> dict[str, Any]:
        insights = self.insights()
        recommendations = self.recommender.prioritize(
            self.recommender.recommend(insights))
        high = sum(1 for insight in insights
                   if insight["severity"] == "high")
        for insight in insights:
            if insight["severity"] == "high":
                self.events.publish(FinanceEventType.RISK_FLAGGED,
                                    {"source": "advisor",
                                     "type": insight["type"]})
        self.metrics.increment("fi.advisor.reports")
        return {
            "insights": insights,
            "recommendations": recommendations,
            "summary": {
                "insights": len(insights),
                "high_severity": high,
                "recommendations": len(recommendations),
            },
        }

    def stats(self) -> dict[str, Any]:
        return {
            "reports": self.metrics.count("fi.advisor.reports"),
            "transactions": self.registry.count_transactions(),
            "alerts": self.registry.count_alerts(),
        }
