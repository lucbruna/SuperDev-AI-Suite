"""Tests for the AI advisor subsystem (Volume 35, Fase 6)."""

from __future__ import annotations

import pytest

from finance_intelligence.advisor.advisor_engine import AdvisorEngine
from finance_intelligence.advisor.insight_generator import InsightGenerator
from finance_intelligence.advisor.recommendation_engine import (
    RecommendationEngine)
from finance_intelligence.budgeting.budget_engine import BudgetEngine
from finance_intelligence.finance_events import FinanceEventType
from finance_intelligence.finance_models import (FinancialAlert, RiskLevel,
                                                 Transaction,
                                                 TransactionType)
from finance_intelligence.finance_protocols import new_id


@pytest.fixture()
def engine() -> AdvisorEngine:
    return AdvisorEngine()


def make_transaction(amount: float,
                     kind: TransactionType = TransactionType.REVENUE,
                     category: str = "") -> Transaction:
    return Transaction(transaction_id=new_id("tx"), amount=amount, kind=kind,
                       metadata={"category_id": category})


class TestInsightGenerator:
    def test_positive_net_position(self, engine: AdvisorEngine) -> None:
        engine.registry.register_transaction(
            make_transaction(1000.0, TransactionType.REVENUE))
        engine.registry.register_transaction(
            make_transaction(400.0, TransactionType.EXPENSE))
        types = {insight["type"] for insight in engine.insights()}
        assert "positive_net_position" in types

    def test_negative_net_position_high_severity(
            self, engine: AdvisorEngine) -> None:
        engine.registry.register_transaction(
            make_transaction(300.0, TransactionType.REVENUE))
        engine.registry.register_transaction(
            make_transaction(900.0, TransactionType.EXPENSE))
        insights = engine.insights()
        negative = next(insight for insight in insights
                        if insight["type"] == "negative_net_position")
        assert negative["severity"] == "high"

    def test_expense_concentration(self, engine: AdvisorEngine) -> None:
        engine.registry.register_transaction(
            make_transaction(900.0, TransactionType.EXPENSE, "infra"))
        engine.registry.register_transaction(
            make_transaction(100.0, TransactionType.EXPENSE, "food"))
        types = {insight["type"] for insight in engine.insights()}
        assert "expense_concentration" in types

    def test_open_alert(self, engine: AdvisorEngine) -> None:
        engine.registry.register_alert(FinancialAlert(
            alert_id=new_id("alert"), level=RiskLevel.HIGH,
            message="cash risk"))
        types = {insight["type"] for insight in engine.insights()}
        assert "open_alert" in types

    def test_budget_overrun(self) -> None:
        budget_engine = BudgetEngine()
        budget = budget_engine.create_budget("2026-07", "marketing", 100.0)
        budget.actual = 150.0
        engine = AdvisorEngine(budget_engine=budget_engine)
        types = {insight["type"] for insight in engine.insights()}
        assert "budget_overrun" in types


class TestRecommendationEngine:
    def test_recommend_maps_insights(self) -> None:
        recommender = RecommendationEngine()
        recommendations = recommender.recommend([
            {"type": "negative_net_position", "severity": "high"},
            {"type": "open_alert", "severity": "high"},
        ])
        actions = {rec["action"] for rec in recommendations}
        assert "increase_revenue_focus" in actions
        assert "review_risk_alerts" in actions

    def test_deduplicates(self) -> None:
        recommender = RecommendationEngine()
        recommendations = recommender.recommend([
            {"type": "open_alert", "severity": "high"},
            {"type": "open_alert", "severity": "high"},
        ])
        assert len(recommendations) == 1

    def test_prioritize_orders_by_priority(self) -> None:
        recommender = RecommendationEngine()
        ordered = recommender.prioritize([
            {"action": "b", "priority": "low"},
            {"action": "a", "priority": "high"},
        ])
        assert ordered[0]["action"] == "a"


class TestAdvisorEngine:
    def test_report_structure(self, engine: AdvisorEngine) -> None:
        engine.registry.register_transaction(
            make_transaction(500.0, TransactionType.EXPENSE))
        engine.registry.register_transaction(
            make_transaction(100.0, TransactionType.REVENUE))
        report = engine.report()
        assert "insights" in report
        assert "recommendations" in report
        assert report["summary"]["insights"] >= 1
        assert report["summary"]["recommendations"] >= 1

    def test_report_publishes_risk_event(self, engine: AdvisorEngine) -> None:
        seen: list[dict] = []
        engine.events.on(FinanceEventType.RISK_FLAGGED, seen.append)
        engine.registry.register_transaction(
            make_transaction(900.0, TransactionType.EXPENSE))
        engine.registry.register_transaction(
            make_transaction(100.0, TransactionType.REVENUE))
        engine.report()
        assert any(payload["source"] == "advisor" for payload in seen)

    def test_stats(self, engine: AdvisorEngine) -> None:
        engine.report()
        stats = engine.stats()
        assert stats["reports"] == 1
        assert stats["transactions"] == 0
