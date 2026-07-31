"""Configuration for the Finance Intelligence Engine (Volume 35)."""

from __future__ import annotations

from typing import Any

from finance_intelligence.finance_models import FiscalRegime


class FinanceConfig:
    """Runtime configuration for the finance engine and its subsystems."""

    def __init__(self, currency: str = "BRL",
                 fiscal_regime: FiscalRegime | str = FiscalRegime.SIMPLES_NACIONAL,
                 approval_threshold: float = 50000.0,
                 fraud_threshold: float = 0.15,
                 budget_alert_threshold: float = 0.9,
                 max_open_alerts: int = 50,
                 fiscal_year: str = "2026",
                 log_level: str = "INFO",
                 **overrides: Any) -> None:
        self.currency = currency
        self.fiscal_regime = FiscalRegime(fiscal_regime)
        self.approval_threshold = float(approval_threshold)
        self.fraud_threshold = float(fraud_threshold)
        self.budget_alert_threshold = float(budget_alert_threshold)
        self.max_open_alerts = int(max_open_alerts)
        self.fiscal_year = fiscal_year
        self.log_level = log_level
        for key, value in overrides.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)

    def merge(self, updates: dict[str, Any] | None) -> "FinanceConfig":
        for key, value in (updates or {}).items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self

    def snapshot(self) -> dict[str, Any]:
        return {
            "currency": self.currency,
            "fiscal_regime": self.fiscal_regime.value,
            "approval_threshold": self.approval_threshold,
            "fraud_threshold": self.fraud_threshold,
            "budget_alert_threshold": self.budget_alert_threshold,
            "max_open_alerts": self.max_open_alerts,
            "fiscal_year": self.fiscal_year,
            "log_level": self.log_level,
        }
