"""Taxation subsystem for the Finance Intelligence Engine (Volume 35)."""

from __future__ import annotations

from finance_intelligence.taxation.fiscal_validation import (
    FiscalValidation)
from finance_intelligence.taxation.tax_calculator import TaxCalculator
from finance_intelligence.taxation.tax_engine import TaxEngine
from finance_intelligence.taxation.tax_reports import TaxReports
from finance_intelligence.taxation.tax_rules import TaxRules

__all__ = [
    "TaxEngine",
    "TaxRules",
    "TaxCalculator",
    "FiscalValidation",
    "TaxReports",
]
