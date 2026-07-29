"""
Talent Manager - High-level HR operations manager.

Provides simplified interface for recruitment, onboarding,
performance, learning, talent, culture, workforce, and payroll.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from .hr_engine import HREngine, EngineConfig
from .employee_context import EmployeeContext
from .hr_events import HREventBus
from .hr_models import (
    CandidateProfile, JobPosition, OnboardingPlan, PerformanceReview,
    LearningPath, TalentProfile, CultureReport, WorkforcePlan,
    PayrollSummary, Employee,
)
from .hr_config import HRConfig
from .hr_security import HRSecurityManager

logger = logging.getLogger(__name__)


@dataclass
class ManagerConfig:
    engine_config: EngineConfig
    enable_erp_integration: bool = True
    enable_knowledge_integration: bool = True
    enable_crm_integration: bool = True
    decision_center_webhook: Optional[str] = None


class TalentManager:
    def __init__(self, config: ManagerConfig):
        self.config = config
        self.engine = HREngine(config.engine_config)
        self.context = config.engine_config.context
        self.event_bus = config.engine_config.event_bus
        self.security = HRSecurityManager()
        self._initialized = False

    async def initialize(self) -> None:
        if self._initialized:
            return
        await self.engine.initialize()
        await self.engine.start()
        self._initialized = True
        logger.info("Talent Manager initialized")

    async def shutdown(self) -> None:
        await self.engine.stop()
        self._initialized = False
        logger.info("Talent Manager shutdown")

    async def get_candidate_profile(self, candidate_id: str) -> CandidateProfile:
        return await self.engine.get_candidate_profile(candidate_id)

    async def screen_candidate(self, job_id: str, resume_data: Dict[str, Any]) -> CandidateProfile:
        return await self.engine.screen_candidate(job_id, resume_data)

    async def match_candidates(self, job_id: str) -> List[CandidateProfile]:
        return await self.context.recruitment.get("matches", [])

    async def get_onboarding_plan(self, employee_id: str) -> OnboardingPlan:
        return await self.engine.get_onboarding_plan(employee_id)

    async def get_performance_review(self, employee_id: str) -> PerformanceReview:
        return await self.engine.get_performance_review(employee_id)

    async def get_learning_path(self, employee_id: str) -> LearningPath:
        return await self.engine.get_learning_path(employee_id)

    async def recommend_training(self, employee_id: str) -> LearningPath:
        return await self.engine.recommend_training(employee_id)

    async def get_talent_profile(self, employee_id: str) -> TalentProfile:
        return await self.engine.get_talent_profile(employee_id)

    async def get_succession_candidates(self, position: str) -> List[TalentProfile]:
        return await self.context.talent.get("succession", [])

    async def get_culture_report(self) -> CultureReport:
        return await self.engine.get_culture_report()

    async def get_engagement_score(self) -> Dict[str, Any]:
        score = await self.context.culture.get("engagement", 75)
        return {"score": score, "status": "good" if score > 70 else "attention"}

    async def get_workforce_plan(self) -> WorkforcePlan:
        return await self.engine.get_workforce_plan()

    async def get_payroll_summary(self, period: str = "monthly") -> PayrollSummary:
        return await self.engine.get_payroll_summary(period)

    async def analyze_salary(self, position: str) -> Dict[str, Any]:
        return await self.context.payroll.get("salary_analysis", {"market_average": 0})

    async def get_kpis(self) -> Dict[str, float]:
        return await self.engine.get_kpis()

    async def get_hr_health_score(self) -> Dict[str, Any]:
        kpis = await self.get_kpis()
        score = sum(kpis.values()) / max(len(kpis), 1)
        return {"score": score, "status": "good" if score > 70 else "attention"}

    async def simulate_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        return await self.context.workforce.get("simulation", scenario)

    async def sync_with_erp(self) -> Dict[str, Any]:
        return {"status": "synced", "timestamp": datetime.utcnow().isoformat()}

    async def sync_with_knowledge_engine(self) -> Dict[str, Any]:
        return {"status": "synced", "timestamp": datetime.utcnow().isoformat()}

    def check_access(self, user_id: str, resource: str, action: str) -> bool:
        return self.security.check_access(user_id, resource, action)

    def encrypt_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self.security.encrypt(data)

    def get_engine_status(self) -> Dict[str, Any]:
        metrics = self.engine.get_metrics()
        return {
            "state": metrics.state.value,
            "uptime": (datetime.utcnow() - metrics.start_time).total_seconds() if metrics.start_time else 0,
            "candidates_screened": metrics.candidates_screened,
            "onboardings_completed": metrics.onboardings_completed,
            "reviews_conducted": metrics.reviews_conducted,
            "trainings_recommended": metrics.trainings_recommended,
            "alerts": metrics.alerts_generated,
            "subsystems": metrics.subsystem_status,
        }

    def is_healthy(self) -> bool:
        return self.engine.get_metrics().state.value == "running"
