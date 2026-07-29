"""
Financial Configuration - Global financial AI engine configuration.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class AccountingConfig:
    auto_classify: bool = True
    auto_reconcile: bool = True
    reconciliation_tolerance: float = 0.01
    fiscal_year_start: str = "01-01"
    default_currency: str = "BRL"
    enable_cost_center_tracking: bool = True


@dataclass
class TreasuryConfig:
    min_cash_balance: float = 100000.0
    max_cash_balance: float = 5000000.0
    auto_invest_surplus: bool = True
    surplus_investment_threshold: float = 1000000.0
    payment_approval_threshold: float = 50000.0
    banking_api_enabled: bool = False


@dataclass
class CashflowConfig:
    forecast_horizon_days: int = 90
    forecast_interval_days: int = 1
    min_history_days: int = 365
    low_cash_warning_days: int = 30
    critical_cash_warning_days: int = 7
    confidence_interval: float = 0.90


@dataclass
class BudgetConfig:
    auto_monitor: bool = True
    deviation_warning_percent: float = 10.0
    deviation_critical_percent: float = 20.0
    budget_approval_required: bool = True
    fiscal_period: str = "monthly"
    rolling_forecast_months: int = 12


@dataclass
class ForecastingConfig:
    revenue_models_enabled: bool = True
    expense_models_enabled: bool = True
    profitability_enabled: bool = True
    scenario_simulation_enabled: bool = True
    monte_carlo_iterations: int = 1000
    confidence_level: float = 0.95


@dataclass
class InvestmentConfig:
    min_roi_threshold: float = 12.0
    max_payback_months: int = 36
    risk_tolerance: str = "moderate"
    portfolio_rebalance_frequency_days: int = 90
    enable_opportunity_scan: bool = True


@dataclass
class RiskConfig:
    enable_fraud_detection: bool = True
    enable_credit_analysis: bool = True
    fraud_sensitivity: str = "medium"
    credit_score_min: int = 300
    credit_score_max: int = 850
    risk_monitoring_interval_hours: int = 6


@dataclass
class AuditConfig:
    enable_auto_audit: bool = True
    audit_frequency_days: int = 30
    anomaly_detection_sensitivity: str = "medium"
    compliance_checklist: List[str] = field(default_factory=lambda: ["lgpd", "sarbanes_oxley", "ifrs"])
    max_transactions_per_audit: int = 10000


@dataclass
class SecurityConfig:
    enable_encryption: bool = True
    enable_access_control: bool = True
    audit_trail_enabled: bool = True
    sensitive_fields: List[str] = field(default_factory=lambda: ["bank_account", "tax_id", "salary", "price"])
    session_timeout_minutes: int = 30


@dataclass
class IntegrationConfig:
    enable_erp_sync: bool = True
    enable_supply_chain_sync: bool = True
    enable_crm_sync: bool = True
    supply_chain_sync_interval_minutes: int = 60
    decision_center_enabled: bool = True


@dataclass
class FinancialConfig:
    engine_name: str = "FinancialAIEngine"
    engine_version: str = "1.0.0"
    environment: str = "production"
    log_level: str = "INFO"
    enable_telemetry: bool = True
    accounting: AccountingConfig = field(default_factory=AccountingConfig)
    treasury: TreasuryConfig = field(default_factory=TreasuryConfig)
    cashflow: CashflowConfig = field(default_factory=CashflowConfig)
    budgeting: BudgetConfig = field(default_factory=BudgetConfig)
    forecasting: ForecastingConfig = field(default_factory=ForecastingConfig)
    investment: InvestmentConfig = field(default_factory=InvestmentConfig)
    risk: RiskConfig = field(default_factory=RiskConfig)
    audit: AuditConfig = field(default_factory=AuditConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    integrations: IntegrationConfig = field(default_factory=IntegrationConfig)
    enable_digital_twin: bool = True
    enable_autonomous_treasury: bool = True
    enable_continuous_learning: bool = True
    _extra: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FinancialConfig":
        config = cls()
        for key, value in data.items():
            if hasattr(config, key) and not key.startswith("_"):
                if isinstance(value, dict) and key in cls.__dataclass_fields__:
                    sub = getattr(config, key)
                    if hasattr(sub, "__dataclass_fields__"):
                        for sk, sv in value.items():
                            if hasattr(sub, sk):
                                setattr(sub, sk, sv)
                        continue
                setattr(config, key, value)
            else:
                config._extra[key] = value
        return config

    @classmethod
    def from_json(cls, path: str) -> "FinancialConfig":
        if not os.path.exists(path):
            return cls()
        with open(path) as f:
            return cls.from_dict(json.load(f))

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self, path: str) -> None:
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2, default=str)

    def validate(self) -> List[str]:
        errors = []
        if self.treasury.min_cash_balance < 0:
            errors.append("min_cash_balance must be positive")
        if self.cashflow.forecast_horizon_days < 1:
            errors.append("forecast_horizon_days must be >= 1")
        if self.investment.min_roi_threshold < 0:
            errors.append("min_roi_threshold must be positive")
        return errors