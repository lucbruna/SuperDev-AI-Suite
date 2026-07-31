"""Tests for the forecasting subsystem (Volume 35, Fase 5)."""

from __future__ import annotations

import pytest

from finance_intelligence.finance_events import FinanceEventType
from finance_intelligence.finance_models import (Transaction,
                                                 TransactionType)
from finance_intelligence.finance_protocols import new_id
from finance_intelligence.forecasting.cash_forecast import CashForecast
from finance_intelligence.forecasting.expense_forecast import (
    ExpenseForecast)
from finance_intelligence.forecasting.forecast_engine import ForecastEngine
from finance_intelligence.forecasting.revenue_forecast import (
    RevenueForecast)


def make_transaction(amount: float,
                     kind: TransactionType = TransactionType.REVENUE
                     ) -> Transaction:
    return Transaction(transaction_id=new_id("tx"), amount=amount, kind=kind)


class TestRevenueForecast:
    def test_value_is_average_times_periods(self) -> None:
        forecast = RevenueForecast().forecast(
            [make_transaction(1000.0), make_transaction(2000.0)],
            periods=3)
        assert forecast.kind == "revenue"
        assert forecast.value == pytest.approx(4500.0)
        assert forecast.horizon == "3m"

    def test_confidence_high_for_stable_data(self) -> None:
        forecast = RevenueForecast().forecast(
            [make_transaction(1000.0), make_transaction(1000.0),
             make_transaction(1000.0)], periods=2)
        assert forecast.confidence == pytest.approx(1.0)

    def test_confidence_lower_for_volatile_data(self) -> None:
        forecast = RevenueForecast().forecast(
            [make_transaction(100.0), make_transaction(10000.0)],
            periods=2)
        assert 0.0 <= forecast.confidence < 1.0

    def test_no_history_defaults(self) -> None:
        forecast = RevenueForecast().forecast([], periods=3)
        assert forecast.value == pytest.approx(0.0)
        assert forecast.confidence == pytest.approx(0.5)


class TestExpenseForecast:
    def test_uses_expense_transactions(self) -> None:
        forecast = ExpenseForecast().forecast(
            [make_transaction(500.0, TransactionType.EXPENSE),
             make_transaction(300.0, TransactionType.PAYMENT)],
            periods=2)
        assert forecast.kind == "expense"
        assert forecast.value == pytest.approx(800.0)

    def test_ignores_revenue(self) -> None:
        forecast = ExpenseForecast().forecast(
            [make_transaction(500.0, TransactionType.EXPENSE),
             make_transaction(9000.0, TransactionType.REVENUE)],
            periods=2)
        assert forecast.value == pytest.approx(1000.0)


class TestCashForecast:
    def test_net_position(self) -> None:
        forecast = CashForecast().forecast(
            [make_transaction(1000.0, TransactionType.REVENUE),
             make_transaction(400.0, TransactionType.EXPENSE)],
            periods=3, opening_balance=100.0)
        assert forecast.kind == "cash"
        assert forecast.value == pytest.approx(1900.0)

    def test_details(self) -> None:
        forecast = CashForecast().forecast(
            [make_transaction(1000.0, TransactionType.REVENUE),
             make_transaction(400.0, TransactionType.EXPENSE)],
            periods=2, opening_balance=0.0)
        assert forecast.details["net_monthly"] == pytest.approx(600.0)


class TestForecastEngine:
    def test_forecast_all(self) -> None:
        engine = ForecastEngine()
        engine.registry.register_transaction(
            make_transaction(1000.0, TransactionType.REVENUE))
        engine.registry.register_transaction(
            make_transaction(400.0, TransactionType.EXPENSE))
        results = engine.forecast(periods=2)
        assert set(results) == {"revenue", "expense", "cash"}
        assert results["revenue"].value == pytest.approx(2000.0)
        assert results["expense"].value == pytest.approx(800.0)

    def test_forecast_single_kind(self) -> None:
        engine = ForecastEngine()
        results = engine.forecast(kind="revenue", periods=2)
        assert set(results) == {"revenue"}

    def test_publishes_event(self) -> None:
        engine = ForecastEngine()
        seen: list[dict] = []
        engine.events.on(FinanceEventType.FORECAST_GENERATED, seen.append)
        engine.forecast()
        assert len(seen) == 1
        assert "revenue" in seen[0]["results"]

    def test_stats(self) -> None:
        engine = ForecastEngine()
        engine.forecast(kind="revenue")
        engine.forecast(kind="expense")
        stats = engine.stats()
        assert stats["generated"] == 2
        assert stats["by_kind"]["revenue"] == 1
        assert stats["by_kind"]["expense"] == 1
        assert stats["by_kind"]["cash"] == 0
