from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from .decision_config import DecisionConfig
from .decision_models import (
    Alert, AlertSeverity, BusinessArea, Dashboard, DashboardType,
    Insight, InsightType, KPI, KpiGroup, Prediction, Recommendation,
    RecommendationPriority, Scenario, ScenarioType, SimulationResult,
)
from .decision_security import DecisionSecurityManager

logger = logging.getLogger(__name__)


class EngineState(Enum):
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class EngineConfig:
    config: DecisionConfig
    security: DecisionSecurityManager
    enable_autonomous: bool = False
    decision_interval_seconds: int = 300
    enable_realtime: bool = True


@dataclass
class EngineMetrics:
    state: EngineState = EngineState.INITIALIZING
    start_time: Optional[datetime] = None
    insights_generated: int = 0
    predictions_made: int = 0
    simulations_run: int = 0
    recommendations_given: int = 0
    decisions_made: int = 0
    alerts_triggered: int = 0
    dashboards_updated: int = 0
    reports_generated: int = 0
    errors: int = 0
    last_action_time: Optional[datetime] = None
    subsystem_status: Dict[str, str] = field(default_factory=dict)


class DecisionEngine:
    def __init__(self, config: EngineConfig):
        self.config = config
        self.metrics = EngineMetrics()
        self._subsystems: Dict[str, Any] = {}
        self._running = False
        self._main_task: Optional[asyncio.Task] = None
        self._decision_loop_task: Optional[asyncio.Task] = None

    async def initialize(self) -> None:
        logger.info("Initializing Decision Command Center...")
        self.metrics.state = EngineState.INITIALIZING
        self.metrics.start_time = datetime.utcnow()
        await self._initialize_subsystems()
        self.metrics.state = EngineState.RUNNING
        logger.info("Decision Command Center initialized")

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._decision_loop_task = asyncio.create_task(self._decision_loop())
        logger.info("Decision Command Center started")

    async def stop(self) -> None:
        logger.info("Stopping Decision Command Center...")
        self._running = False
        if self._decision_loop_task:
            self._decision_loop_task.cancel()
            try:
                await self._decision_loop_task
            except asyncio.CancelledError:
                pass
        await self._shutdown_subsystems()
        self.metrics.state = EngineState.STOPPED
        logger.info("Decision Command Center stopped")

    async def pause(self) -> None:
        self._running = False
        self.metrics.state = EngineState.PAUSED

    async def resume(self) -> None:
        if not self._running:
            self._running = True
            self._decision_loop_task = asyncio.create_task(self._decision_loop())
            self.metrics.state = EngineState.RUNNING

    async def _initialize_subsystems(self) -> None:
        from .dashboards.dashboard_engine import DashboardEngine
        from .indicators.indicator_engine import IndicatorEngine
        from .analytics.analytics_engine import AnalyticsEngine
        from .prediction.prediction_engine import PredictionEngine
        from .simulation.simulation_engine import SimulationEngine
        from .recommendations.recommendation_engine import RecommendationEngine
        from .executive.executive_engine import ExecutiveEngine

        self._subsystems = {
            "dashboards": DashboardEngine(self.config.config, self.config.security),
            "indicators": IndicatorEngine(self.config.config, self.config.security),
            "analytics": AnalyticsEngine(self.config.config, self.config.security),
            "prediction": PredictionEngine(self.config.config, self.config.security),
            "simulation": SimulationEngine(self.config.config, self.config.security),
            "recommendations": RecommendationEngine(self.config.config, self.config.security),
            "executive": ExecutiveEngine(self.config.config, self.config.security),
        }
        for name, sub in self._subsystems.items():
            await sub.initialize()
            self.metrics.subsystem_status[name] = "initialized"

    async def _decision_loop(self) -> None:
        while self._running:
            try:
                if self.config.enable_autonomous:
                    await self._make_autonomous_decisions()
                await asyncio.sleep(self.config.decision_interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Decision loop error: {e}")
                self.metrics.errors += 1
                await asyncio.sleep(60)

    async def _make_autonomous_decisions(self) -> None:
        alerts = await self._subsystems["analytics"].detect_anomalies()
        for alert in alerts:
            if alert.severity in (AlertSeverity.CRITICAL, AlertSeverity.HIGH):
                await self._subsystems["recommendations"].generate_for_alert(alert)

    async def get_kpis(self) -> Dict[str, float]:
        return await self._subsystems["indicators"].get_all_values()

    async def get_insights(self) -> List[Insight]:
        self.metrics.insights_generated += 1
        return await self._subsystems["analytics"].get_insights()

    async def get_predictions(self) -> List[Prediction]:
        self.metrics.predictions_made += 1
        return await self._subsystems["prediction"].get_all_predictions()

    async def run_simulation(self, scenario: Scenario) -> SimulationResult:
        self.metrics.simulations_run += 1
        return await self._subsystems["simulation"].execute(scenario)

    async def get_recommendations(self) -> List[Recommendation]:
        self.metrics.recommendations_given += 1
        return await self._subsystems["recommendations"].get_all()

    async def get_dashboards(self) -> List[Dashboard]:
        return await self._subsystems["dashboards"].get_all()

    async def get_executive_summary(self) -> Dict[str, Any]:
        self.metrics.reports_generated += 1
        return await self._subsystems["executive"].generate_summary()

    async def get_alerts(self) -> List[Alert]:
        return await self._subsystems["analytics"].get_active_alerts()

    def get_metrics(self) -> EngineMetrics:
        return self.metrics

    def get_subsystem(self, name: str):
        return self._subsystems.get(name)

    async def _shutdown_subsystems(self) -> None:
        for name, sub in self._subsystems.items():
            try:
                await sub.shutdown()
                self.metrics.subsystem_status[name] = "stopped"
            except Exception as e:
                logger.error(f"Error shutting down {name}: {e}")
