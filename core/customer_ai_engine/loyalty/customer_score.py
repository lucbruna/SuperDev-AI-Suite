"""
Customer Score - Calculate customer lifetime value and loyalty scores.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..customer_context import CustomerContext
from ..customer_events import CustomerEventBus
from ..customer_models import LoyaltyTier, CustomerTier
from ..customer_config import CustomerConfig

logger = logging.getLogger(__name__)


class CustomerScore:
    def __init__(self, config: CustomerConfig, context: CustomerContext, event_bus: CustomerEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self._tiers: Dict[str, LoyaltyTier] = {}

    def get_tier(self, customer_id: str) -> LoyaltyTier:
        if customer_id not in self._tiers:
            self._tiers[customer_id] = LoyaltyTier(
                customer_id=customer_id,
                tier=CustomerTier.BRONZE,
                points=0,
                points_to_next=1000,
                lifetime_value=0.0,
                join_date=datetime.utcnow(),
            )
        return self._tiers[customer_id]

    def add_points(self, customer_id: str, points: int) -> LoyaltyTier:
        tier = self.get_tier(customer_id)
        tier.points += points
        tier.lifetime_value += points * 0.01
        self._update_tier(tier)
        return tier

    def calculate_clv(self, customer_id: str) -> float:
        tier = self.get_tier(customer_id)
        return tier.lifetime_value

    def _update_tier(self, tier: LoyaltyTier) -> None:
        tier_map = [
            (50000, CustomerTier.DIAMOND),
            (20000, CustomerTier.PLATINUM),
            (5000, CustomerTier.GOLD),
            (1000, CustomerTier.SILVER),
        ]
        new_tier = CustomerTier.BRONZE
        for points_needed, next_tier in tier_map:
            if tier.points >= points_needed:
                new_tier = next_tier
                break
        tier.tier = new_tier
        tier.points_to_next = self._points_to_next(new_tier)

    def _points_to_next(self, current: CustomerTier) -> int:
        tier_points = {
            CustomerTier.BRONZE: 1000,
            CustomerTier.SILVER: 5000,
            CustomerTier.GOLD: 20000,
            CustomerTier.PLATINUM: 50000,
            CustomerTier.DIAMOND: 0,
        }
        return tier_points.get(current, 0)
