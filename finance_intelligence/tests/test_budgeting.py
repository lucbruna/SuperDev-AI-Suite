"""Tests for the budgeting subsystem (Volume 35, Fase 6)."""

from __future__ import annotations

import pytest

from finance_intelligence.budgeting.budget_engine import BudgetEngine
from finance_intelligence.budgeting.budget_manager import BudgetManager
from finance_intelligence.finance_events import FinanceEventType
from finance_intelligence.finance_models import Budget


@pytest.fixture()
def engine() -> BudgetEngine:
    return BudgetEngine()


class TestBudgetManager:
    def test_create(self, engine: BudgetEngine) -> None:
        budget = engine.create_budget("2026-07", "marketing", 1000.0,
                                      owner="ana")
        assert budget.planned == pytest.approx(1000.0)
        assert budget.owner == "ana"
        assert engine.manager.get(budget.budget_id) is budget

    def test_create_publishes_event(self, engine: BudgetEngine) -> None:
        seen: list[dict] = []
        engine.events.on(FinanceEventType.BUDGET_CREATED, seen.append)
        engine.create_budget("2026-07", "marketing", 1000.0)
        assert len(seen) == 1
        assert seen[0]["category"] == "marketing"

    def test_monitor_statuses(self, engine: BudgetEngine) -> None:
        on_track = Budget(budget_id="b1", period="2026-07",
                          category="a", planned=100.0, actual=50.0)
        warning = Budget(budget_id="b2", period="2026-07",
                         category="b", planned=100.0, actual=80.0)
        over = Budget(budget_id="b3", period="2026-07",
                      category="c", planned=100.0, actual=150.0)
        assert engine.manager.monitor(on_track)["status"] == "on_track"
        assert engine.manager.monitor(warning)["status"] == "warning"
        assert engine.manager.monitor(over)["status"] == "over"

    def test_monitor_publishes_alert_over_threshold(
            self, engine: BudgetEngine) -> None:
        seen: list[dict] = []
        engine.events.on(FinanceEventType.BUDGET_ALERT, seen.append)
        budget = Budget(budget_id="b1", period="2026-07",
                        category="a", planned=100.0, actual=90.0)
        engine.manager.monitor(budget)
        assert len(seen) == 1
        assert seen[0]["budget_id"] == "b1"

    def test_remove(self, engine: BudgetEngine) -> None:
        budget = engine.create_budget("2026-07", "x", 100.0)
        assert engine.manager.remove(budget.budget_id) is True
        assert engine.manager.get(budget.budget_id) is None


class TestBudgetControl:
    def test_remaining_and_can_spend(self, engine: BudgetEngine) -> None:
        budget = engine.create_budget("2026-07", "x", 100.0)
        assert engine.control.remaining(budget) == pytest.approx(100.0)
        assert engine.control.can_spend(budget, 60.0) is True
        assert engine.control.can_spend(budget, 150.0) is False

    def test_allow_spend_within_budget(self, engine: BudgetEngine) -> None:
        budget = engine.create_budget("2026-07", "x", 100.0)
        assert engine.record_spend(budget.budget_id, 40.0) is True
        assert budget.actual == pytest.approx(40.0)

    def test_allow_spend_denied_over_budget(self, engine: BudgetEngine) -> None:
        budget = engine.create_budget("2026-07", "x", 100.0)
        assert engine.record_spend(budget.budget_id, 150.0) is False
        assert budget.actual == pytest.approx(0.0)

    def test_over_budgets(self, engine: BudgetEngine) -> None:
        budget = engine.create_budget("2026-07", "x", 100.0)
        budget.actual = 120.0
        assert engine.control.over_budgets() == [budget]


class TestBudgetAnalysis:
    def test_utilization_summary(self, engine: BudgetEngine) -> None:
        on_track = engine.create_budget("2026-07", "a", 100.0)
        on_track.actual = 50.0
        over = engine.create_budget("2026-07", "b", 100.0)
        over.actual = 150.0
        summary = engine.analysis.utilization_summary()
        assert summary["on_track"] == 1
        assert summary["over"] == 1

    def test_top_over_budget(self, engine: BudgetEngine) -> None:
        small = engine.create_budget("2026-07", "a", 100.0)
        small.actual = 110.0
        big = engine.create_budget("2026-07", "b", 100.0)
        big.actual = 200.0
        top = engine.analysis.top_over_budget()
        assert top[0].budget_id == big.budget_id

    def test_totals(self, engine: BudgetEngine) -> None:
        engine.create_budget("2026-07", "a", 100.0)
        engine.create_budget("2026-07", "b", 200.0)
        totals = engine.analysis.totals()
        assert totals["planned"] == pytest.approx(300.0)
        assert totals["actual"] == pytest.approx(0.0)


class TestBudgetEngine:
    def test_monitor_all(self, engine: BudgetEngine) -> None:
        engine.create_budget("2026-07", "a", 100.0)
        engine.create_budget("2026-07", "b", 100.0)
        reports = engine.monitor_all()
        assert len(reports) == 2

    def test_monitor_missing(self, engine: BudgetEngine) -> None:
        assert engine.monitor("missing")["status"] == "missing"

    def test_stats(self, engine: BudgetEngine) -> None:
        engine.create_budget("2026-07", "a", 100.0)
        stats = engine.stats()
        assert stats["budgets"] == 1
        assert stats["created"] == 1
