"""
Lead Analyzer - Score and qualify sales leads using multi-factor analysis.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..customer_context import CustomerContext
from ..customer_events import CustomerEventBus
from ..customer_models import LeadScore
from ..customer_config import CustomerConfig

logger = logging.getLogger(__name__)


class LeadAnalyzer:
    def __init__(self, config: CustomerConfig, context: CustomerContext, event_bus: CustomerEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus

    def calculate(self, customer_data: Dict[str, Any]) -> LeadScore:
        score = 0.0
        weights = {
            "email": 5,
            "phone": 5,
            "name": 5,
            "interactions": 20,
            "page_views": 10,
            "time_on_site": 10,
            "cart_value": 15,
            "returning_visitor": 10,
        }
        filled_fields = sum(1 for k in weights if k in customer_data and customer_data.get(k))
        score += (filled_fields / len(weights)) * 30
        interactions = customer_data.get("interactions", 0)
        score += min(interactions * 5, 25)
        page_views = customer_data.get("page_views", 0)
        score += min(page_views * 2, 15)
        cart_value = customer_data.get("cart_value", 0)
        if cart_value > 500:
            score += 15
        elif cart_value > 100:
            score += 10
        elif cart_value > 0:
            score += 5
        if customer_data.get("returning_visitor", False):
            score += 10
        engagement = "low"
        if score >= 70:
            engagement = "high"
        elif score >= 40:
            engagement = "medium"
        return LeadScore(
            customer_id=customer_data.get("id", "unknown"),
            score=min(score, 100),
            engagement_level=engagement,
            purchase_intent=score / 100,
            likelihood_to_buy=score / 100 * 0.8,
        )

    def segment(self, score: LeadScore) -> str:
        if score.score >= 80:
            return "hot"
        elif score.score >= 50:
            return "warm"
        return "cold"

    def get_scoring_factors(self) -> Dict[str, float]:
        return {
            "profile_completion": 0.30,
            "engagement": 0.25,
            "browsing_behavior": 0.15,
            "cart_value": 0.15,
            "return_visits": 0.10,
            "recency": 0.05,
        }
