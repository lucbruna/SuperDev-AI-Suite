"""Tests for the cashflow subsystem (Volume 35, Fase 2)."""

from __future__ import annotations

from finance_intelligence.cashflow import CashflowEngine
from finance_intelligence.finance_events import (FinanceEventType,
                                                 FinanceEvents)
from finance_intelligence.finance_models import TransactionType
from finance_intelligence.finance_registry import FinanceRegistry


class TestInflowOutflow:
    def _engine(self):
        return CashflowEngine()

    def test_register_inflow(self):
        engine = self._engine()
        transaction = engine.inflows.register(
            "venda de produto", 1500.0, source="Cliente A",
            scheduled_for=5)
        assert transaction.kind == TransactionType.REVENUE
        assert engine.inflows.total() == 1500.0
        assert len(engine.inflows.list_inflows()) == 1

    def test_register_outflow(self):
        engine = self._engine()
        transaction = engine.outflows.register(
            "aluguel", 800.0, payee="Imobiliária", scheduled_for=10)
        assert transaction.kind == TransactionType.EXPENSE
        assert engine.outflows.total() == 800.0

    def test_projected_within_horizon(self):
        engine = self._engine()
        engine.inflows.register("a", 100.0, scheduled_for=5)
        engine.inflows.register("b", 50.0, scheduled_for=60)
        assert engine.inflows.projected(horizon_days=30) == 100.0


class TestCashProjection:
    def test_projection_math(self):
        engine = CashflowEngine()
        inflow = engine.inflows.register("venda", 500.0, scheduled_for=1)
        outflow = engine.outflows.register("custo", 200.0, scheduled_for=2)
        forecast = engine.projection.project(
            opening_balance=1000.0, horizon_days=3,
            inflows=[inflow], outflows=[outflow])
        assert forecast.kind == "cashflow"
        assert forecast.horizon == "3d"
        assert forecast.value == 1300.0
        assert forecast.details["opening_balance"] == 1000.0
        assert forecast.details["min_balance"] == 1000.0
        assert forecast.details["max_balance"] == 1500.0

    def test_projection_publishes_event(self):
        engine = CashflowEngine()
        fired = []
        engine.events.on(FinanceEventType.FORECAST_GENERATED,
                         lambda payload: fired.append(payload))
        engine.projection.project(1000.0, horizon_days=5)
        assert len(fired) == 1
        assert fired[0]["value"] == 1000.0

    def test_series(self):
        engine = CashflowEngine()
        forecast = engine.projection.project(100.0, horizon_days=2)
        days = engine.projection.series(forecast)
        assert len(days) == 2
        assert days[1]["balance"] == 100.0


class TestLiquidityAnalysis:
    def test_healthy(self):
        engine = CashflowEngine()
        inflow = engine.inflows.register("venda", 1000.0)
        outflow = engine.outflows.register("custo", 400.0)
        result = engine.liquidity.analyze(
            500.0, [inflow], [outflow])
        assert result["status"] == "healthy"
        assert result["closing_balance"] == 1100.0
        assert result["liquidity_ratio"] == 2.5

    def test_critical_publishes_event(self):
        engine = CashflowEngine()
        outflow = engine.outflows.register("prejuízo", 2000.0)
        fired = []
        engine.events.on(FinanceEventType.RISK_FLAGGED,
                         lambda payload: fired.append(payload))
        result = engine.liquidity.analyze(100.0, [], [outflow])
        assert result["status"] == "critical"
        assert len(fired) == 1
        assert fired[0]["source"] == "liquidity"

    def test_monthly_summary(self):
        engine = CashflowEngine()
        import time
        jan = time.mktime((2026, 1, 15, 0, 0, 0, 0, 0, 0))
        engine.inflows.register("a", 100.0, scheduled_for=1)
        engine.inflows.list_inflows()[0].created_at = jan
        summary = engine.liquidity.monthly_summary(
            engine.inflows.list_inflows())
        assert summary["count"] == 1
        assert summary["months"]["2026-01"]["inflows"] == 100.0


class TestCashflowEngine:
    def test_facade_delegates(self):
        engine = CashflowEngine()
        engine.register_inflow("venda", 1000.0, scheduled_for=1)
        engine.register_outflow("custo", 300.0, scheduled_for=2)
        forecast = engine.project(500.0, horizon_days=3)
        assert forecast.value == 1200.0
        analysis = engine.analyze(500.0)
        assert analysis["total_inflows"] == 1000.0
        assert analysis["total_outflows"] == 300.0

    def test_stats(self):
        engine = CashflowEngine()
        engine.register_inflow("venda", 100.0)
        engine.register_outflow("custo", 40.0)
        stats = engine.stats()
        assert stats["inflows"] == 100.0
        assert stats["outflows"] == 40.0
        assert stats["net"] == 60.0

    def test_standalone_engine_has_defaults(self):
        engine = CashflowEngine()
        assert isinstance(engine.registry, FinanceRegistry)
        assert isinstance(engine.events, FinanceEvents)
