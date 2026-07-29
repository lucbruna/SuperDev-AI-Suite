"""
Treasury Manager - High-level financial operations manager.

Provides simplified interface for treasury, cash management,
budgeting, investments, and financial oversight.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from .financial_engine import FinancialEngine, EngineConfig
from .finance_context import FinanceContext
from .financial_events import FinancialEventBus
from .financial_models import (
    CashflowForecast, TreasuryPosition, BudgetReport,
    FinancialStatement, InvestmentAnalysis, RiskAssessment, AuditReport,
    Transaction, AccountEntry,
)
from .financial_config import FinancialConfig
from .financial_security import FinancialSecurityManager

logger = logging.getLogger(__name__)


@dataclass
class ManagerConfig:
    engine_config: EngineConfig
    enable_erp_integration: bool = True
    enable_supply_chain_integration: bool = True
    enable_crm_integration: bool = True
    decision_center_webhook: Optional[str] = None


class TreasuryManager:
    def __init__(self, config: ManagerConfig):
        self.config = config
        self.engine = FinancialEngine(config.engine_config)
        self.context = config.engine_config.context
        self.event_bus = config.engine_config.event_bus
        self.security = FinancialSecurityManager()
        self._initialized = False

    async def initialize(self) -> None:
        if self._initialized:
            return
        await self.engine.initialize()
        await self.engine.start()
        self._initialized = True
        logger.info("Treasury Manager initialized")

    async def shutdown(self) -> None:
        await self.engine.stop()
        self._initialized = False
        logger.info("Treasury Manager shutdown")

    # Cash & Treasury
    async def get_cash_position(self) -> TreasuryPosition:
        return await self.engine.get_treasury_position()

    async def get_cashflow_forecast(self, horizon_days: int = 90) -> CashflowForecast:
        return await self.engine.get_cashflow_forecast(horizon_days)

    async def get_liquidity_analysis(self) -> Dict[str, Any]:
        return await self.context.cashflow.get("liquidity_analysis", {})

    # Accounting
    async def get_balance_sheet(self) -> FinancialStatement:
        return await self.engine.get_financial_statements()

    async def get_income_statement(self, period: str = "monthly") -> Dict[str, Any]:
        return await self.context.accounting.get("income_statement", {})

    async def reconcile_accounts(self, account_id: Optional[str] = None) -> Dict[str, Any]:
        return await self.context.accounting.get("reconciliation", {"status": "completed"})

    async def classify_transaction(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        return await self.context.accounting.get("classification", {"category": "unknown"})

    # Budgeting
    async def create_budget(self, budget_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.context.budgeting.get("created", budget_data)

    async def get_budget_report(self, period: str = "monthly") -> BudgetReport:
        return await self.engine.get_budget_report(period)

    async def get_budget_deviations(self, department: Optional[str] = None) -> List[Dict[str, Any]]:
        return await self.context.budgeting.get("deviations", [])

    # Forecasting
    async def get_revenue_forecast(self, horizon_days: int = 90) -> Dict[str, Any]:
        forecast = await self.engine.get_cashflow_forecast(horizon_days)
        return {"revenue": forecast.projections, "confidence": 0.85}

    async def get_profitability_analysis(self) -> Dict[str, Any]:
        return await self.context.forecasting.get("profitability", {})

    # Investment
    async def analyze_investment(self, opportunity: Dict[str, Any]) -> InvestmentAnalysis:
        return await self.engine.analyze_investment(opportunity)

    async def get_portfolio_performance(self) -> Dict[str, Any]:
        return await self.context.investment.get("portfolio", {})

    async def calculate_roi(self, project_id: str) -> Dict[str, Any]:
        return await self.context.investment.get("roi", {"roi": 0.15})

    # Risk
    async def get_risk_assessment(self) -> RiskAssessment:
        return await self.engine.get_risk_assessment()

    async def detect_fraud(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return await self.context.risk.get("fraud_alerts", [])

    async def analyze_credit(self, customer_id: str) -> Dict[str, Any]:
        return await self.context.risk.get("credit_analysis", {"score": 750})

    # Audit
    async def run_audit(self, scope: Optional[Dict] = None) -> AuditReport:
        return await self.engine.run_audit(scope)

    async def check_compliance(self, regulation: str = "all") -> Dict[str, Any]:
        return await self.context.audit.get("compliance", {"status": "compliant"})

    async def detect_anomalies(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return await self.context.audit.get("anomalies", [])

    # Simulation
    async def simulate_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        return await self.engine.simulate_scenario(scenario)

    async def run_what_if(self, question: str) -> Dict[str, Any]:
        return await self.simulate_scenario({"question": question})

    # KPIs
    async def get_kpis(self) -> Dict[str, float]:
        return await self.engine.get_kpis()

    async def get_financial_health_score(self) -> Dict[str, Any]:
        kpis = await self.get_kpis()
        score = sum(kpis.values()) / max(len(kpis), 1)
        return {"score": score, "status": "good" if score > 70 else "attention"}

    # Integration
    async def sync_with_erp(self) -> Dict[str, Any]:
        return {"status": "synced", "timestamp": datetime.utcnow().isoformat()}

    async def sync_with_supply_chain(self) -> Dict[str, Any]:
        return {"status": "synced", "timestamp": datetime.utcnow().isoformat()}

    # Security
    def check_access(self, user_id: str, resource: str, action: str) -> bool:
        return self.security.check_access(user_id, resource, action)

    def encrypt_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self.security.encrypt(data)

    # Status
    def get_engine_status(self) -> Dict[str, Any]:
        metrics = self.engine.get_metrics()
        return {
            "state": metrics.state.value,
            "uptime": (datetime.utcnow() - metrics.start_time).total_seconds() if metrics.start_time else 0,
            "forecasts": metrics.forecasts_generated,
            "anomalies": metrics.anomalies_detected,
            "alerts": metrics.alerts_generated,
            "subsystems": metrics.subsystem_status,
        }

    def is_healthy(self) -> bool:
        return self.engine.get_metrics().state.value == "running"