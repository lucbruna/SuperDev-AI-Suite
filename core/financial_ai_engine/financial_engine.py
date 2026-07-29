"""
Financial AI Engine - Core orchestration engine.

Coordinates treasury, accounting, investment, risk, and audit intelligence.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from .finance_context import FinanceContext
from .financial_events import FinancialEvent, FinancialEventBus, EventType
from .financial_models import (
    CashflowForecast, FinancialStatement, InvestmentAnalysis,
    BudgetReport, RiskAssessment, AuditReport, TreasuryPosition,
)
from .financial_config import FinancialConfig
from .financial_metrics import KPICalculator

logger = logging.getLogger(__name__)


class EngineState(Enum):
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class EngineConfig:
    config: FinancialConfig
    event_bus: FinancialEventBus
    context: FinanceContext
    auto_treasury: bool = True
    forecasting_enabled: bool = True
    risk_monitoring_enabled: bool = True
    auto_approval_threshold: float = 50000.0
    decision_interval_seconds: int = 600
    enable_autonomous_mode: bool = False


@dataclass
class EngineMetrics:
    state: EngineState = EngineState.INITIALIZING
    start_time: Optional[datetime] = None
    forecasts_generated: int = 0
    reconciliations_run: int = 0
    anomalies_detected: int = 0
    budgets_monitored: int = 0
    investments_analyzed: int = 0
    alerts_generated: int = 0
    errors: int = 0
    last_forecast_time: Optional[datetime] = None
    subsystem_status: Dict[str, str] = field(default_factory=dict)


class FinancialEngine:
    def __init__(self, config: EngineConfig):
        self.config = config
        self.metrics = EngineMetrics()
        self._subsystems: Dict[str, Any] = {}
        self._running = False
        self._main_task: Optional[asyncio.Task] = None
        self._decision_loop_task: Optional[asyncio.Task] = None

    async def initialize(self) -> None:
        logger.info("Initializing Financial AI Engine...")
        self.metrics.state = EngineState.INITIALIZING
        self.metrics.start_time = datetime.utcnow()
        await self._initialize_subsystems()
        await self._register_event_handlers()
        self.metrics.state = EngineState.RUNNING
        logger.info("Financial AI Engine initialized")

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._decision_loop_task = asyncio.create_task(self._decision_loop())
        logger.info("Financial AI Engine started")

    async def stop(self) -> None:
        logger.info("Stopping Financial AI Engine...")
        self._running = False
        if self._decision_loop_task:
            self._decision_loop_task.cancel()
            try: await self._decision_loop_task
            except asyncio.CancelledError: pass
        await self._shutdown_subsystems()
        self.metrics.state = EngineState.STOPPED
        logger.info("Financial AI Engine stopped")

    async def pause(self) -> None:
        self._running = False
        self.metrics.state = EngineState.PAUSED

    async def resume(self) -> None:
        if not self._running:
            self._running = True
            self._decision_loop_task = asyncio.create_task(self._decision_loop())
            self.metrics.state = EngineState.RUNNING

    async def _initialize_subsystems(self) -> None:
        from .accounting.accounting_engine import AccountingEngine
        from .treasury.treasury_engine import TreasuryEngine
        from .cashflow.cashflow_engine import CashflowEngine
        from .budgeting.budget_engine import BudgetEngine
        from .forecasting.forecasting_engine import ForecastingEngine
        from .investment.investment_engine import InvestmentEngine
        from .risk.financial_risk_engine import FinancialRiskEngine
        from .audit.financial_audit_engine import FinancialAuditEngine

        self._subsystems = {
            "accounting": AccountingEngine(self.config.config, self.config.context, self.config.event_bus),
            "treasury": TreasuryEngine(self.config.config, self.config.context, self.config.event_bus),
            "cashflow": CashflowEngine(self.config.config, self.config.context, self.config.event_bus),
            "budgeting": BudgetEngine(self.config.config, self.config.context, self.config.event_bus),
            "forecasting": ForecastingEngine(self.config.config, self.config.context, self.config.event_bus),
            "investment": InvestmentEngine(self.config.config, self.config.context, self.config.event_bus),
            "risk": FinancialRiskEngine(self.config.config, self.config.context, self.config.event_bus),
            "audit": FinancialAuditEngine(self.config.config, self.config.context, self.config.event_bus),
        }
        for name, sub in self._subsystems.items():
            await sub.initialize()
            self.metrics.subsystem_status[name] = "initialized"

    async def _register_event_handlers(self) -> None:
        self.config.event_bus.subscribe(EventType.CASH_CRITICAL, self._handle_cash_critical)
        self.config.event_bus.subscribe(EventType.ANOMALY_DETECTED, self._handle_anomaly)
        self.config.event_bus.subscribe(EventType.BUDGET_DEVIATION, self._handle_budget_deviation)
        self.config.event_bus.subscribe(EventType.FRAUD_SUSPECTED, self._handle_fraud_suspected)

    async def _decision_loop(self) -> None:
        while self._running:
            try:
                if self.config.enable_autonomous_mode:
                    await self._make_autonomous_decisions()
                await asyncio.sleep(self.config.decision_interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Decision loop error: {e}")
                self.metrics.errors += 1
                await asyncio.sleep(60)

    async def _make_autonomous_decisions(self) -> None:
        treasury = await self._subsystems["treasury"].get_position()
        forecast = await self._subsystems["forecasting"].get_forecast(90)
        if treasury.cash_balance < self.config.config.treasury.min_cash_balance:
            await self._subsystems["treasury"].generate_alert("CASH_LOW")

    async def _handle_cash_critical(self, event: FinancialEvent) -> None:
        self.metrics.alerts_generated += 1
        await self._subsystems["treasury"].handle_cash_crisis(event.payload)

    async def _handle_anomaly(self, event: FinancialEvent) -> None:
        self.metrics.anomalies_detected += 1
        await self._subsystems["audit"].investigate(event.payload)

    async def _handle_budget_deviation(self, event: FinancialEvent) -> None:
        self.metrics.alerts_generated += 1
        await self._subsystems["budgeting"].handle_deviation(event.payload)

    async def _handle_fraud_suspected(self, event: FinancialEvent) -> None:
        self.metrics.alerts_generated += 1
        await self._subsystems["risk"].investigate_fraud(event.payload)

    async def _shutdown_subsystems(self) -> None:
        for name, sub in self._subsystems.items():
            try:
                await sub.shutdown()
                self.metrics.subsystem_status[name] = "stopped"
            except Exception as e:
                logger.error(f"Error shutting down {name}: {e}")

    async def get_cashflow_forecast(self, horizon_days: int = 90) -> CashflowForecast:
        self.metrics.forecasts_generated += 1
        return await self._subsystems["cashflow"].forecast(horizon_days)

    async def get_treasury_position(self) -> TreasuryPosition:
        return await self._subsystems["treasury"].get_position()

    async def get_budget_report(self, period: str = "monthly") -> BudgetReport:
        return await self._subsystems["budgeting"].get_report(period)

    async def get_financial_statements(self) -> FinancialStatement:
        return await self._subsystems["accounting"].get_statements()

    async def analyze_investment(self, opportunity: Dict[str, Any]) -> InvestmentAnalysis:
        self.metrics.investments_analyzed += 1
        return await self._subsystems["investment"].analyze(opportunity)

    async def get_risk_assessment(self) -> RiskAssessment:
        return await self._subsystems["risk"].assess()

    async def run_audit(self, scope: Optional[Dict] = None) -> AuditReport:
        return await self._subsystems["audit"].run(scope)

    async def simulate_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        return await self._subsystems["forecasting"].simulate(scenario)

    async def get_kpis(self) -> Dict[str, float]:
        calc = KPICalculator(self.config.context)
        return await calc.calculate_all()

    def get_metrics(self) -> EngineMetrics:
        return self.metrics

    def get_subsystem(self, name: str):
        return self._subsystems.get(name)