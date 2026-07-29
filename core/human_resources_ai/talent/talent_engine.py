"""
Talent Engine - Core talent intelligence coordination.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..employee_context import EmployeeContext
from ..hr_events import HREvent, HREventBus, EventType
from ..hr_models import TalentProfile, CareerPath, SuccessionPlan, RiskLevel
from ..hr_config import HRConfig
from .skill_graph import SkillGraph
from .career_planner import CareerPlanner
from .succession import SuccessionPlanner

logger = logging.getLogger(__name__)


class TalentEngine:
    def __init__(self, config: HRConfig, context: EmployeeContext, event_bus: HREventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self.graph: Optional[SkillGraph] = None
        self.career: Optional[CareerPlanner] = None
        self.succession: Optional[SuccessionPlanner] = None

    async def initialize(self) -> None:
        self.graph = SkillGraph(self.config, self.context, self.event_bus)
        self.career = CareerPlanner(self.config, self.context, self.event_bus)
        self.succession = SuccessionPlanner(self.config, self.context, self.event_bus)
        logger.info("TalentEngine initialized")

    async def get_profile(self, employee_id: str) -> TalentProfile:
        return TalentProfile(
            employee_id=employee_id, employee_name="Employee",
            position="Analyst", potential_score=82.0,
        )

    async def identify_high_potential(self) -> List[TalentProfile]:
        return [TalentProfile(employee_id="EMP-001", employee_name="João", position="Developer", potential_score=90.0)]

    async def handle_turnover_risk(self, payload: Dict[str, Any]) -> None:
        logger.info(f"Turnover risk handled: {payload}")

    async def shutdown(self) -> None:
        logger.info("TalentEngine shutdown")
