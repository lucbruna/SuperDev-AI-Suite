"""
Offer Generator - Create personalized sales offers and promotions.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..customer_context import CustomerContext
from ..customer_events import CustomerEventBus
from ..customer_models import Recommendation
from ..customer_config import CustomerConfig

logger = logging.getLogger(__name__)


class OfferGenerator:
    def __init__(self, config: CustomerConfig, context: CustomerContext, event_bus: CustomerEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus

    def create_offer(self, customer_id: str, product: str, discount_percent: float) -> Dict[str, Any]:
        return {
            "id": str(uuid.uuid4()),
            "customer_id": customer_id,
            "product": product,
            "discount_percent": discount_percent,
            "valid_until": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "status": "active",
        }

    def generate_bundle(self, main_product: str, accessories: List[str]) -> Dict[str, Any]:
        return {
            "bundle_id": str(uuid.uuid4()),
            "main_product": main_product,
            "accessories": accessories,
            "bundle_discount": 10.0,
            "type": "cross_sell",
        }

    def create_personalized_offer(self, customer_id: str, lead_score: float) -> Dict[str, Any]:
        if lead_score >= 80:
            return self.create_offer(customer_id, "membership_premium", 20.0)
        elif lead_score >= 50:
            return self.create_offer(customer_id, "first_purchase", 15.0)
        return self.create_offer(customer_id, "welcome", 10.0)
