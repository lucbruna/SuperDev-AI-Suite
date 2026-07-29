"""
Personalization Engine - Build and manage intelligent customer profiles.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..customer_context import CustomerContext
from ..customer_events import CustomerEvent, CustomerEventBus, EventType
from ..customer_models import CustomerProfile, CustomerTier
from ..customer_config import CustomerConfig
from .customer_profile import CustomerProfileManager
from .behavior_analysis import BehaviorAnalysis
from .recommendation_engine import RecommendationEngine as PersonalizationRecommender

logger = logging.getLogger(__name__)


class PersonalizationEngine:
    def __init__(self, config: CustomerConfig, context: CustomerContext, event_bus: CustomerEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self.profiles: Optional[CustomerProfileManager] = None
        self.behavior: Optional[BehaviorAnalysis] = None
        self.recommender: Optional[PersonalizationRecommender] = None

    async def initialize(self) -> None:
        self.profiles = CustomerProfileManager(self.config, self.context, self.event_bus)
        self.behavior = BehaviorAnalysis(self.config, self.context, self.event_bus)
        self.recommender = PersonalizationRecommender(self.config, self.context, self.event_bus)
        logger.info("PersonalizationEngine initialized")

    async def get_profile(self, customer_id: str) -> CustomerProfile:
        profile = self.profiles.get(customer_id)
        if not profile:
            profile = self.profiles.create(customer_id)
        return profile

    async def update_profile(self, customer_id: str, data: Dict[str, Any]) -> CustomerProfile:
        profile = self.profiles.update(customer_id, data)
        await self.event_bus.publish(CustomerEvent(
            event_type=EventType.PROFILE_UPDATED,
            payload={"customer_id": customer_id},
        ))
        return profile

    async def track_behavior(self, customer_id: str, event_type: str, data: Dict[str, Any]) -> None:
        self.behavior.track(customer_id, event_type, data)
        self.context.personalization.set(f"behavior_{customer_id}", data)

    async def shutdown(self) -> None:
        logger.info("PersonalizationEngine shutdown")
