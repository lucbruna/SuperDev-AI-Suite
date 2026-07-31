"""Taxation subsystem facade (Volume 35).

Aggregates tax rules, calculation, fiscal validation and tax reports.
"""

from __future__ import annotations

from typing import Any

from finance_intelligence.finance_events import FinanceEvents
from finance_intelligence.finance_metrics import FinanceMetrics
from finance_intelligence.finance_models import FiscalRegime, Transaction
from finance_intelligence.finance_registry import FinanceRegistry
from finance_intelligence.taxation.fiscal_validation import (
    FiscalValidation)
from finance_intelligence.taxation.tax_calculator import TaxCalculator
from finance_intelligence.taxation.tax_reports import TaxReports
from finance_intelligence.taxation.tax_rules import TaxRules


class TaxEngine:
    """Aggregate facade over the taxation subsystems."""

    def __init__(self, registry: FinanceRegistry | None = None,
                 events: FinanceEvents | None = None,
                 metrics: FinanceMetrics | None = None,
                 regime: FiscalRegime | str = FiscalRegime.SIMPLES_NACIONAL
                 ) -> None:
        self.registry = registry or FinanceRegistry()
        self.events = events or FinanceEvents()
        self.metrics = metrics or FinanceMetrics()
        if isinstance(regime, str):
            regime = FiscalRegime(regime)
        self.rules = TaxRules(regime)
        self.calculator = TaxCalculator(self.registry, self.events,
                                        self.metrics, self.rules)
        self.validation = FiscalValidation(self.rules)
        self.reports = TaxReports()

    # -- conveniences --------------------------------------------------------
    def calculate(self, transaction: Transaction,
                  period: str = ""):
        return self.calculator.calculate(transaction, period)

    def calculate_all(self, period: str = ""):
        return self.calculator.calculate_all(period)

    def summary(self):
        return self.reports.summary(self.calculator.list())

    def validate(self, declared_amount: float, period: str = ""):
        return self.validation.validate(
            self.registry.list_transactions(), declared_amount, period)

    def stats(self) -> dict[str, Any]:
        return {
            "regime": self.rules.regime.value,
            "taxes_calculated": self.metrics.count("fi.taxes.calculated"),
            "total": self.calculator.total(),
            "applicable_taxes": self.rules.applicable_taxes(),
        }
