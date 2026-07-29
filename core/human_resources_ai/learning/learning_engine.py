"""
Learning Engine - Core learning intelligence coordination.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..employee_context import EmployeeContext
from ..hr_events import HREvent, HREventBus, EventType
from ..hr_models import LearningPath, TrainingModule
from ..hr_config import HRConfig
from .training_recommender import TrainingRecommender
from .knowledge_path import KnowledgePath
from .skill_development import SkillDevelopment

logger = logging.getLogger(__name__)


class LearningEngine:
    def __init__(self, config: HRConfig, context: EmployeeContext, event_bus: HREventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self.recommender: Optional[TrainingRecommender] = None
        self.paths: Optional[KnowledgePath] = None
        self.skills: Optional[SkillDevelopment] = None

    async def initialize(self) -> None:
        self.recommender = TrainingRecommender(self.config, self.context, self.event_bus)
        self.paths = KnowledgePath(self.config, self.context, self.event_bus)
        self.skills = SkillDevelopment(self.config, self.context, self.event_bus)
        logger.info("LearningEngine initialized")

    async def get_path(self, employee_id: str) -> LearningPath:
        return LearningPath(employee_id=employee_id, employee_name="Employee", position="Unknown")

    async def recommend(self, employee_id: str) -> LearningPath:
        path = LearningPath(
            employee_id=employee_id, employee_name="Employee", position="Unknown",
            modules=[TrainingModule(id="T-001", title="Leadership 101", duration_hours=8.0)],
        )
        await self.event_bus.publish(HREvent(
            event_type=EventType.LEARNING_PATH_UPDATED,
            payload={"employee_id": employee_id, "modules": len(path.modules)},
        ))
        return path

    async def shutdown(self) -> None:
        logger.info("LearningEngine shutdown")
