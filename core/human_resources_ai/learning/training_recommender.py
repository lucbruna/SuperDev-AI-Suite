"""
Training Recommender - AI-powered training recommendations.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..employee_context import EmployeeContext
from ..hr_events import HREventBus
from ..hr_models import LearningPath, TrainingModule
from ..hr_config import HRConfig

logger = logging.getLogger(__name__)


class TrainingRecommender:
    def __init__(self, config: HRConfig, context: EmployeeContext, event_bus: HREventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus

    def recommend_for_role(self, position: str, current_skills: List[str]) -> LearningPath:
        return LearningPath(
            employee_id="EMP-001", employee_name="Employee", position=position,
            modules=[
                TrainingModule(id="TM-1", title="Software Architecture", duration_hours=16.0),
                TrainingModule(id="TM-2", title="Advanced Database", duration_hours=12.0),
                TrainingModule(id="TM-3", title="Cloud Computing", duration_hours=20.0),
            ],
        )

    def identify_gaps(self, required_skills: List[str], current_skills: List[str]) -> List[str]:
        return [s for s in required_skills if s not in current_skills]
