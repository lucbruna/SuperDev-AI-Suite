"""
Training Plan - Create personalized onboarding training plans.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..employee_context import EmployeeContext
from ..hr_events import HREventBus
from ..hr_models import OnboardingPlan, TrainingModule
from ..hr_config import HRConfig

logger = logging.getLogger(__name__)


class TrainingPlan:
    def __init__(self, config: HRConfig, context: EmployeeContext, event_bus: HREventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus

    def generate_plan(self, position: str, department: str) -> OnboardingPlan:
        return OnboardingPlan(
            employee_id="new",
            employee_name="New Employee",
            position=position,
            duration_days=self.config.onboarding.default_duration_days,
            phases=[
                {"week": 1, "focus": "Internal systems", "tasks": ["Setup", "Orientation"]},
                {"week": 2, "focus": "Processes", "tasks": ["Process training", "Shadowing"]},
                {"week": 3, "focus": "Supervised execution", "tasks": ["Guided work", "Mentoring"]},
                {"week": 4, "focus": "Evaluation", "tasks": ["Assessment", "Feedback"]},
            ],
        )

    def assign_modules(self, employee_id: str, modules: List[TrainingModule]) -> None:
        logger.info(f"Assigned {len(modules)} training modules to {employee_id}")
