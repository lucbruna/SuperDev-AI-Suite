from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from .decision_engine import DecisionEngine, EngineConfig
from .decision_config import DecisionConfig
from .decision_security import DecisionSecurityManager
from .decision_models import (
    Alert, BoardReport, Dashboard, ExecutiveSummary, Insight,
    KPI, Prediction, Recommendation, Scenario, SimulationResult,
)

logger = logging.getLogger(__name__)


@dataclass
class ManagerConfig:
    engine_config: EngineConfig
    enable_erp_integration: bool = True
    enable_finance_integration: bool = True
    enable_crm_integration: bool = True
    decision_webhook: Optional[str] = None


class CommandCenter:
    def __init__(self, config: ManagerConfig):
        self.config = config
        self.engine = DecisionEngine(config.engine_config)
        self.security = config.engine_config.security
        self._initialized = False

    async def initialize(self) -> None:
        if self._initialized:
            return
        await self.engine.initialize()
        await self.engine.start()
        self._initialized = True
        logger.info("Command Center initialized")

    async def shutdown(self) -> None:
        await self.engine.stop()
        self._initialized = False
        logger.info("Command Center shutdown")

    async def get_kpis(self) -> Dict[str, float]:
        return await self.engine.get_kpis()

    async def get_kpi_report(self) -> List[KPI]:
        return await self.engine._subsystems["indicators"].get_all_kpis()

    async def get_insights(self) -> List[Insight]:
        return await self.engine.get_insights()

    async def get_predictions(self) -> List[Prediction]:
        return await self.engine.get_predictions()

    async def run_simulation(self, scenario: Scenario) -> SimulationResult:
        return await self.engine.run_simulation(scenario)

    async def get_recommendations(self) -> List[Recommendation]:
        return await self.engine.get_recommendations()

    async def get_dashboards(self) -> List[Dashboard]:
        return await self.engine.get_dashboards()

    async def get_executive_summary(self) -> ExecutiveSummary:
        result = await self.engine.get_executive_summary()
        return ExecutiveSummary(**result) if isinstance(result, dict) else result

    async def get_board_report(self) -> BoardReport:
        result = await self.engine._subsystems["executive"].generate_board_report()
        return BoardReport(**result) if isinstance(result, dict) else result

    async def get_alerts(self) -> List[Alert]:
        return await self.engine.get_alerts()

    async def ask_ceo_assistant(self, question: str) -> Dict[str, Any]:
        return await self.engine._subsystems["executive"].ceo_query(question)

    async def get_business_health(self) -> Dict[str, Any]:
        kpis = await self.get_kpis()
        alerts = await self.get_alerts()
        score = sum(kpis.values()) / max(len(kpis), 1) if kpis else 0
        critical = sum(1 for a in alerts if a.severity.value == "critical")
        return {
            "health_score": round(score, 1),
            "status": "good" if score > 70 else "attention" if score > 40 else "critical",
            "total_kpis": len(kpis),
            "active_alerts": len(alerts),
            "critical_alerts": critical,
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def simulate_strategy(self, strategy_params: Dict[str, Any]) -> SimulationResult:
        scenario = Scenario(
            id="strategy-sim",
            name=strategy_params.get("name", "Strategy Simulation"),
            scenario_type="simulation",
            parameters=strategy_params,
        )
        return await self.engine.run_simulation(scenario)

    async def sync_with_erp(self) -> Dict[str, Any]:
        return {"status": "synced", "timestamp": datetime.utcnow().isoformat()}

    async def sync_with_finance(self) -> Dict[str, Any]:
        return {"status": "synced", "timestamp": datetime.utcnow().isoformat()}

    async def sync_with_crm(self) -> Dict[str, Any]:
        return {"status": "synced", "timestamp": datetime.utcnow().isoformat()}

    def check_access(self, user_id: str, resource: str, action: str) -> bool:
        return self.security.check_access(user_id, resource, action)

    def set_user_role(self, user_id: str, role: str) -> None:
        self.security.set_user_role(user_id, role)

    def get_engine_status(self) -> Dict[str, Any]:
        metrics = self.engine.get_metrics()
        return {
            "state": metrics.state.value,
            "uptime": (datetime.utcnow() - metrics.start_time).total_seconds() if metrics.start_time else 0,
            "insights": metrics.insights_generated,
            "predictions": metrics.predictions_made,
            "simulations": metrics.simulations_run,
            "recommendations": metrics.recommendations_given,
            "decisions": metrics.decisions_made,
            "alerts": metrics.alerts_triggered,
            "reports": metrics.reports_generated,
            "subsystems": metrics.subsystem_status,
        }

    def is_healthy(self) -> bool:
        return self.engine.get_metrics().state.value == "running"
