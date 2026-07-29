"""
Loyalty Engine - Core loyalty intelligence coordination.

Manages loyalty tiers, rewards, customer scoring, and retention.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..customer_context import CustomerContext
from ..customer_events import CustomerEvent, CustomerEventBus, EventType
from ..customer_models import LoyaltyTier, CustomerTier
from ..customer_config import CustomerConfig
from .reward_manager import RewardManager
from .customer_score import CustomerScore
from .retention import RetentionManager

logger = logging.getLogger(__name__)


class LoyaltyEngine:
    def __init__(self, config: CustomerConfig, context: CustomerContext, event_bus: CustomerEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self.rewards: Optional[RewardManager] = None
        self.scoring: Optional[CustomerScore] = None
        self.retention: Optional[RetentionManager] = None

    async def initialize(self) -> None:
        self.rewards = RewardManager(self.config, self.context, self.event_bus)
        self.scoring = CustomerScore(self.config, self.context, self.event_bus)
        self.retention = RetentionManager(self.config, self.context, self.event_bus)
        logger.info("LoyaltyEngine initialized")

    async def get_status(self, customer_id: str) -> LoyaltyTier:
        return self.scoring.get_tier(customer_id)

    async def add_points(self, customer_id: str, amount: float) -> LoyaltyTier:
        points = int(amount * self.config.loyalty.points_per_currency_spent)
        tier = self.scoring.add_points(customer_id, points)
        return tier

    async def handle_risk(self, payload: Dict[str, Any]) -> None:
        customer_id = payload.get("customer_id")
        if customer_id:
            self.retention.mark_at_risk(customer_id)

    async def shutdown(self) -> None:
        logger.info("LoyaltyEngine shutdown")
