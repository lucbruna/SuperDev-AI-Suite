"""
Policy Engine - Core policy management coordination.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..legal_context import LegalContext
from ..legal_events import LegalEvent, LegalEventBus, EventType
from ..legal_models import PolicyDocument
from ..legal_config import LegalConfig
from .policy_creator import PolicyCreator
from .policy_validator import PolicyValidator
from .employee_acknowledgment import EmployeeAcknowledgment

logger = logging.getLogger(__name__)


class PolicyEngine:
    def __init__(self, config: LegalConfig, context: LegalContext, event_bus: LegalEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self.creator: Optional[PolicyCreator] = None
        self.validator: Optional[PolicyValidator] = None
        self.acknowledgment: Optional[EmployeeAcknowledgment] = None

    async def initialize(self) -> None:
        self.creator = PolicyCreator(self.config, self.context, self.event_bus)
        self.validator = PolicyValidator(self.config, self.context, self.event_bus)
        self.acknowledgment = EmployeeAcknowledgment(self.config, self.context, self.event_bus)
        logger.info("PolicyEngine initialized")

    async def get_policy(self, policy_id: str) -> PolicyDocument:
        return PolicyDocument(id=policy_id, title="Company Policy")

    async def publish_policy(self, policy: PolicyDocument) -> PolicyDocument:
        await self.event_bus.publish(LegalEvent(
            event_type=EventType.POLICY_PUBLISHED,
            payload={"policy_id": policy.id, "title": policy.title},
        ))
        return policy

    async def shutdown(self) -> None:
        logger.info("PolicyEngine shutdown")
