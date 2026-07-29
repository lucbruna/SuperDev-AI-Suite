"""
HR AI Engine - Core orchestration engine.

Coordinates recruitment, onboarding, performance, learning,
talent, culture, workforce, and payroll intelligence.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from .employee_context import EmployeeContext
from .hr_events import HREvent, HREventBus, EventType
from .hr_models import (
    CandidateProfile, JobPosition, OnboardingPlan, PerformanceReview,
    LearningPath, TalentProfile, CultureReport, WorkforcePlan,
    PayrollSummary,
)
from .hr_config import HRConfig
from .hr_metrics import KPICalculator

logger = logging.getLogger(__name__)


class EngineState(Enum):
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class EngineConfig:
    config: HRConfig
    event_bus: HREventBus
    context: EmployeeContext
    auto_recruitment: bool = True
    learning_enabled: bool = True
    culture_monitoring_enabled: bool = True
    auto_approval_threshold: float = 50000.0
    decision_interval_seconds: int = 600
    enable_autonomous_mode: bool = False


@dataclass
class EngineMetrics:
    state: EngineState = EngineState.INITIALIZING
    start_time: Optional[datetime] = None
    candidates_screened: int = 0
    onboardings_completed: int = 0
    reviews_conducted: int = 0
    trainings_recommended: int = 0
    talents_mapped: int = 0
    culture_surveys: int = 0
    workforce_plans: int = 0
    payrolls_processed: int = 0
    alerts_generated: int = 0
    errors: int = 0
    last_action_time: Optional[datetime] = None
    subsystem_status: Dict[str, str] = field(default_factory=dict)


class HREngine:
    def __init__(self, config: EngineConfig):
        self.config = config
        self.metrics = EngineMetrics()
        self._subsystems: Dict[str, Any] = {}
        self._running = False
        self._main_task: Optional[asyncio.Task] = None
        self._decision_loop_task: Optional[asyncio.Task] = None

    async def initialize(self) -> None:
        logger.info("Initializing HR AI Engine...")
        self.metrics.state = EngineState.INITIALIZING
        self.metrics.start_time = datetime.utcnow()
        await self._initialize_subsystems()
        await self._register_event_handlers()
        self.metrics.state = EngineState.RUNNING
        logger.info("HR AI Engine initialized")

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._decision_loop_task = asyncio.create_task(self._decision_loop())
        logger.info("HR AI Engine started")

    async def stop(self) -> None:
        logger.info("Stopping HR AI Engine...")
        self._running = False
        if self._decision_loop_task:
            self._decision_loop_task.cancel()
            try: await self._decision_loop_task
            except asyncio.CancelledError: pass
        await self._shutdown_subsystems()
        self.metrics.state = EngineState.STOPPED
        logger.info("HR AI Engine stopped")

    async def pause(self) -> None:
        self._running = False
        self.metrics.state = EngineState.PAUSED

    async def resume(self) -> None:
        if not self._running:
            self._running = True
            self._decision_loop_task = asyncio.create_task(self._decision_loop())
            self.metrics.state = EngineState.RUNNING

    async def _initialize_subsystems(self) -> None:
        from .recruitment.recruitment_engine import RecruitmentEngine
        from .onboarding.onboarding_engine import OnboardingEngine
        from .performance.performance_engine import PerformanceEngine
        from .learning.learning_engine import LearningEngine
        from .talent.talent_engine import TalentEngine
        from .culture.culture_engine import CultureEngine
        from .workforce.workforce_engine import WorkforceEngine
        from .payroll.payroll_engine import PayrollEngine

        self._subsystems = {
            "recruitment": RecruitmentEngine(self.config.config, self.config.context, self.config.event_bus),
            "onboarding": OnboardingEngine(self.config.config, self.config.context, self.config.event_bus),
            "performance": PerformanceEngine(self.config.config, self.config.context, self.config.event_bus),
            "learning": LearningEngine(self.config.config, self.config.context, self.config.event_bus),
            "talent": TalentEngine(self.config.config, self.config.context, self.config.event_bus),
            "culture": CultureEngine(self.config.config, self.config.context, self.config.event_bus),
            "workforce": WorkforceEngine(self.config.config, self.config.context, self.config.event_bus),
            "payroll": PayrollEngine(self.config.config, self.config.context, self.config.event_bus),
        }
        for name, sub in self._subsystems.items():
            await sub.initialize()
            self.metrics.subsystem_status[name] = "initialized"

    async def _register_event_handlers(self) -> None:
        self.config.event_bus.subscribe(EventType.CANDIDATE_MATCHED, self._handle_candidate_matched)
        self.config.event_bus.subscribe(EventType.PERFORMANCE_ANOMALY, self._handle_performance_anomaly)
        self.config.event_bus.subscribe(EventType.CULTURE_DECLINE, self._handle_culture_decline)
        self.config.event_bus.subscribe(EventType.TURNOVER_RISK, self._handle_turnover_risk)

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
        engagement = await self._subsystems["culture"].get_engagement_score()
        if engagement < 60:
            await self._subsystems["culture"].generate_alert("ENGAGEMENT_LOW")

    async def _handle_candidate_matched(self, event: HREvent) -> None:
        self.metrics.alerts_generated += 1
        await self._subsystems["recruitment"].handle_match(event.payload)

    async def _handle_performance_anomaly(self, event: HREvent) -> None:
        self.metrics.alerts_generated += 1
        await self._subsystems["performance"].investigate(event.payload)

    async def _handle_culture_decline(self, event: HREvent) -> None:
        self.metrics.alerts_generated += 1
        await self._subsystems["culture"].handle_decline(event.payload)

    async def _handle_turnover_risk(self, event: HREvent) -> None:
        self.metrics.alerts_generated += 1
        await self._subsystems["talent"].handle_turnover_risk(event.payload)

    async def _shutdown_subsystems(self) -> None:
        for name, sub in self._subsystems.items():
            try:
                await sub.shutdown()
                self.metrics.subsystem_status[name] = "stopped"
            except Exception as e:
                logger.error(f"Error shutting down {name}: {e}")

    async def get_candidate_profile(self, candidate_id: str) -> CandidateProfile:
        return await self._subsystems["recruitment"].get_profile(candidate_id)

    async def get_onboarding_plan(self, employee_id: str) -> OnboardingPlan:
        return await self._subsystems["onboarding"].get_plan(employee_id)

    async def get_performance_review(self, employee_id: str) -> PerformanceReview:
        return await self._subsystems["performance"].get_review(employee_id)

    async def get_learning_path(self, employee_id: str) -> LearningPath:
        return await self._subsystems["learning"].get_path(employee_id)

    async def get_talent_profile(self, employee_id: str) -> TalentProfile:
        return await self._subsystems["talent"].get_profile(employee_id)

    async def get_culture_report(self) -> CultureReport:
        return await self._subsystems["culture"].get_report()

    async def get_workforce_plan(self) -> WorkforcePlan:
        return await self._subsystems["workforce"].get_plan()

    async def get_payroll_summary(self, period: str = "monthly") -> PayrollSummary:
        return await self._subsystems["payroll"].get_summary(period)

    async def screen_candidate(self, job_id: str, candidate_data: Dict[str, Any]) -> CandidateProfile:
        self.metrics.candidates_screened += 1
        return await self._subsystems["recruitment"].screen(job_id, candidate_data)

    async def recommend_training(self, employee_id: str) -> LearningPath:
        self.metrics.trainings_recommended += 1
        return await self._subsystems["learning"].recommend(employee_id)

    async def get_kpis(self) -> Dict[str, float]:
        calc = KPICalculator(self.config.context)
        return await calc.calculate_all()

    def get_metrics(self) -> EngineMetrics:
        return self.metrics

    def get_subsystem(self, name: str):
        return self._subsystems.get(name)
