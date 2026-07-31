"""Tests for the taxation subsystem (Volume 35, Fase 4)."""

from __future__ import annotations

import pytest

from finance_intelligence.finance_models import (FiscalRegime, Transaction,
                                                 TransactionType)
from finance_intelligence.finance_protocols import new_id
from finance_intelligence.taxation.tax_calculator import TaxCalculator
from finance_intelligence.taxation.tax_engine import TaxEngine
from finance_intelligence.taxation.tax_reports import TaxReports
from finance_intelligence.taxation.tax_rules import TaxRules


def make_transaction(amount: float, revenue: bool = True) -> Transaction:
    return Transaction(
        transaction_id=new_id("tx"),
        amount=amount,
        kind=TransactionType.REVENUE if revenue else TransactionType.EXPENSE)


class TestTaxRules:
    def test_rates_simples(self) -> None:
        rules = TaxRules(FiscalRegime.SIMPLES_NACIONAL)
        assert rules.rate("SIMPLES") == pytest.approx(0.06)
        assert rules.rate("PIS") == 0.0

    def test_rates_lucro_presumido(self) -> None:
        rules = TaxRules(FiscalRegime.LUCRO_PRESUMIDO)
        assert rules.applies("PIS")
        assert rules.rate("PIS") == pytest.approx(0.0065)

    def test_rates_lucro_real(self) -> None:
        rules = TaxRules(FiscalRegime.LUCRO_REAL)
        assert rules.applies("IRPJ")
        assert rules.rate("IRPJ") == pytest.approx(0.25)

    def test_applicable_taxes(self) -> None:
        rules = TaxRules(FiscalRegime.SIMPLES_NACIONAL)
        assert "SIMPLES" in rules.applicable_taxes()
        assert "IRPJ" not in rules.applicable_taxes()

    def test_set_regime(self) -> None:
        rules = TaxRules()
        rules.set_regime(FiscalRegime.LUCRO_REAL)
        assert rules.applies("CSLL")


class TestTaxCalculator:
    def test_calculate_simples(self) -> None:
        engine = TaxEngine(regime=FiscalRegime.SIMPLES_NACIONAL)
        record = engine.calculate(make_transaction(1000.0))
        assert record.amount == pytest.approx(60.0)
        assert record.kind == "SIMPLES"

    def test_calculate_lucro_presumido(self) -> None:
        engine = TaxEngine(regime=FiscalRegime.LUCRO_PRESUMIDO)
        record = engine.calculate(make_transaction(1000.0))
        assert record.kind == "PIS"
        assert record.amount == pytest.approx(6.5)

    def test_expense_not_taxable(self) -> None:
        engine = TaxEngine(regime=FiscalRegime.SIMPLES_NACIONAL)
        record = engine.calculate(
            make_transaction(1000.0, revenue=False))
        assert record.amount == pytest.approx(0.0)

    def test_calculate_all(self) -> None:
        engine = TaxEngine(regime=FiscalRegime.SIMPLES_NACIONAL)
        engine.registry.register_transaction(make_transaction(1000.0))
        engine.registry.register_transaction(make_transaction(2000.0))
        records = engine.calculator.calculate_all("2026-07")
        assert len(records) == 2
        assert engine.calculator.total("2026-07") == pytest.approx(180.0)

    def test_period_filter(self) -> None:
        engine = TaxEngine(regime=FiscalRegime.SIMPLES_NACIONAL)
        engine.calculate(make_transaction(1000.0), "2026-07")
        engine.calculate(make_transaction(1000.0), "2026-08")
        assert engine.calculator.total("2026-07") == pytest.approx(60.0)


class TestFiscalValidation:
    def test_compliant(self) -> None:
        engine = TaxEngine()
        engine.registry.register_transaction(make_transaction(1000.0))
        result = engine.validate(declared_amount=1000.0)
        assert result["compliant"] is True

    def test_non_compliant(self) -> None:
        engine = TaxEngine()
        engine.registry.register_transaction(make_transaction(1000.0))
        result = engine.validate(declared_amount=800.0)
        assert result["compliant"] is False
        assert result["difference"] == pytest.approx(-200.0)

    def test_checks(self) -> None:
        engine = TaxEngine()
        checks = engine.validation.checks(
            engine.registry.list_transactions())
        assert checks["has_transactions"] is False
        assert checks["regime_configured"] is True


class TestTaxReports:
    def test_summary(self) -> None:
        engine = TaxEngine(regime=FiscalRegime.SIMPLES_NACIONAL)
        engine.calculate(make_transaction(1000.0), "2026-07")
        engine.calculate(make_transaction(2000.0), "2026-07")
        summary = engine.reports.summary(engine.calculator.list())
        assert summary["total"] == pytest.approx(180.0)
        assert summary["record_count"] == 2
        assert summary["by_kind"]["SIMPLES"] == pytest.approx(180.0)

    def test_by_period(self) -> None:
        engine = TaxEngine(regime=FiscalRegime.SIMPLES_NACIONAL)
        engine.calculate(make_transaction(1000.0), "2026-07")
        engine.calculate(make_transaction(1000.0), "2026-08")
        periods = engine.reports.by_period(engine.calculator.list())
        assert periods["2026-07"] == pytest.approx(60.0)
        assert periods["2026-08"] == pytest.approx(60.0)

    def test_obligation(self) -> None:
        engine = TaxEngine(regime=FiscalRegime.SIMPLES_NACIONAL)
        engine.calculate(make_transaction(1000.0))
        obligation = engine.reports.obligation(
            engine.calculator.list(), regime="simples")
        assert obligation["due"] is True
        assert obligation["total_obligation"] == pytest.approx(60.0)


class TestTaxEngine:
    def test_engine_from_string_regime(self) -> None:
        engine = TaxEngine(regime="simples_nacional")
        assert engine.rules.regime == FiscalRegime.SIMPLES_NACIONAL

    def test_stats(self) -> None:
        engine = TaxEngine()
        engine.calculate(make_transaction(1000.0))
        stats = engine.stats()
        assert stats["regime"] == "simples_nacional"
        assert stats["total"] == pytest.approx(60.0)
        assert stats["taxes_calculated"] == 1
