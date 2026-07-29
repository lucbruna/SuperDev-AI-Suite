"""
Customer Profile Manager - Build, store, and update customer profiles.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..customer_context import CustomerContext
from ..customer_events import CustomerEventBus
from ..customer_models import CustomerProfile, CustomerTier
from ..customer_config import CustomerConfig

logger = logging.getLogger(__name__)


class CustomerProfileManager:
    def __init__(self, config: CustomerConfig, context: CustomerContext, event_bus: CustomerEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self._profiles: Dict[str, CustomerProfile] = {}

    def create(self, customer_id: str, name: str = "", email: str = "") -> CustomerProfile:
        profile = CustomerProfile(
            id=customer_id,
            name=name,
            email=email,
            tier=CustomerTier.BRONZE,
        )
        self._profiles[customer_id] = profile
        self.context.personalization.set(f"profile_{customer_id}", {"id": customer_id, "name": name, "tier": "bronze"})
        logger.info(f"Profile created: {customer_id}")
        return profile

    def get(self, customer_id: str) -> Optional[CustomerProfile]:
        return self._profiles.get(customer_id)

    def update(self, customer_id: str, data: Dict[str, Any]) -> CustomerProfile:
        profile = self.get(customer_id)
        if not profile:
            profile = self.create(customer_id)
        for key, value in data.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        self._profiles[customer_id] = profile
        self.context.personalization.set(f"profile_{customer_id}", data)
        return profile

    def add_segment(self, customer_id: str, segment: str) -> None:
        profile = self.get(customer_id)
        if profile and segment not in profile.segments:
            profile.segments.append(segment)

    def add_tag(self, customer_id: str, tag: str) -> None:
        profile = self.get(customer_id)
        if profile and tag not in profile.tags:
            profile.tags.append(tag)

    def update_tier(self, customer_id: str, tier: CustomerTier) -> None:
        profile = self.get(customer_id)
        if profile:
            profile.tier = tier

    def get_by_segment(self, segment: str) -> List[CustomerProfile]:
        return [p for p in self._profiles.values() if segment in p.segments]

    def get_by_tier(self, tier: CustomerTier) -> List[CustomerProfile]:
        return [p for p in self._profiles.values() if p.tier == tier]
