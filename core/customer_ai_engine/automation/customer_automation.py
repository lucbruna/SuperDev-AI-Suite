"""
Customer Automation - Core automation and campaign coordination.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..customer_context import CustomerContext
from ..customer_events import CustomerEvent, CustomerEventBus, EventType
from ..customer_models import Campaign, CampaignStatus
from ..customer_config import CustomerConfig
from .campaign_engine import CampaignEngine
from .trigger_manager import TriggerManager
from .workflow import WorkflowEngine

logger = logging.getLogger(__name__)


class CustomerAutomation:
    def __init__(self, config: CustomerConfig, context: CustomerContext, event_bus: CustomerEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self.campaigns: Optional[CampaignEngine] = None
        self.triggers: Optional[TriggerManager] = None
        self.workflows: Optional[WorkflowEngine] = None

    async def initialize(self) -> None:
        self.campaigns = CampaignEngine(self.config, self.context, self.event_bus)
        self.triggers = TriggerManager(self.config, self.context, self.event_bus)
        self.workflows = WorkflowEngine(self.config, self.context, self.event_bus)
        logger.info("CustomerAutomation initialized")

    async def run_campaign(self, campaign: Campaign) -> Campaign:
        result = await self.campaigns.execute(campaign)
        await self.event_bus.publish(CustomerEvent(
            event_type=EventType.CAMPAIGN_STARTED,
            payload={"campaign_id": campaign.id, "name": campaign.name},
        ))
        return result

    async def trigger_retention_campaign(self) -> None:
        logger.info("Retention campaign triggered autonomously")

    async def shutdown(self) -> None:
        logger.info("CustomerAutomation shutdown")
