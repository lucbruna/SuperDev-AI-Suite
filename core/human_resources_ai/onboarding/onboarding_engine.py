"""
Onboarding Engine - Core onboarding intelligence coordination.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..employee_context import EmployeeContext
from ..hr_events import HREvent, HREventBus, EventType
from ..hr_models import OnboardingPlan, TrainingModule
from ..hr_config import HRConfig
from .employee_setup import EmployeeSetup
from .training_plan import TrainingPlan
from .document_manager import DocumentManager

logger = logging.getLogger(__name__)


class OnboardingEngine:
    def __init__(self, config: HRConfig, context: EmployeeContext, event_bus: HREventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self.setup: Optional[EmployeeSetup] = None
        self.training: Optional[TrainingPlan] = None
        self.documents: Optional[DocumentManager] = None

    async def initialize(self) -> None:
        self.setup = EmployeeSetup(self.config, self.context, self.event_bus)
        self.training = TrainingPlan(self.config, self.context, self.event_bus)
        self.documents = DocumentManager(self.config, self.context, self.event_bus)
        logger.info("OnboardingEngine initialized")

    async def get_plan(self, employee_id: str) -> OnboardingPlan:
        return OnboardingPlan(employee_id=employee_id, employee_name="New Employee", position="Unknown")

    async def create_plan(self, employee_id: str, position: str) -> OnboardingPlan:
        plan = OnboardingPlan(employee_id=employee_id, employee_name="New Employee", position=position)
        await self.event_bus.publish(HREvent(
            event_type=EventType.ONBOARDING_STARTED,
            payload={"employee_id": employee_id, "position": position},
        ))
        return plan

    async def shutdown(self) -> None:
        logger.info("OnboardingEngine shutdown")
