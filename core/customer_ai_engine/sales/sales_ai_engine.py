"""
Sales AI Engine - Core sales intelligence coordination.

Analyzes leads, generates recommendations, and predicts conversions.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..customer_context import CustomerContext
from ..customer_events import CustomerEvent, CustomerEventBus, EventType
from ..customer_models import LeadScore, Recommendation, ChannelType
from ..customer_config import CustomerConfig
from .lead_analyzer import LeadAnalyzer
from .recommendation import RecommendationEngine
from .offer_generator import OfferGenerator
from .conversion_predictor import ConversionPredictor

logger = logging.getLogger(__name__)


class SalesAIEngine:
    def __init__(self, config: CustomerConfig, context: CustomerContext, event_bus: CustomerEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self.leads: Optional[LeadAnalyzer] = None
        self.recommender: Optional[RecommendationEngine] = None
        self.offers: Optional[OfferGenerator] = None
        self.predictor: Optional[ConversionPredictor] = None

    async def initialize(self) -> None:
        self.leads = LeadAnalyzer(self.config, self.context, self.event_bus)
        self.recommender = RecommendationEngine(self.config, self.context, self.event_bus)
        self.offers = OfferGenerator(self.config, self.context, self.event_bus)
        self.predictor = ConversionPredictor(self.config, self.context, self.event_bus)
        logger.info("SalesAIEngine initialized")

    async def score_lead(self, customer_data: Dict[str, Any]) -> LeadScore:
        score = self.leads.calculate(customer_data)
        if score.score >= self.config.sales.min_lead_score_for_action:
            await self.event_bus.publish(CustomerEvent(
                event_type=EventType.LEAD_QUALIFIED,
                payload={"customer_id": customer_data.get("id"), "score": score.score},
            ))
        return score

    async def recommend(self, customer_id: str) -> List[Recommendation]:
        profile = self.context.personalization.get(f"profile_{customer_id}", {})
        recommendations = self.recommender.generate(customer_id, profile)
        return recommendations

    async def handle_opportunity(self, payload: Dict[str, Any]) -> None:
        logger.info(f"Sales opportunity: {payload}")

    async def shutdown(self) -> None:
        logger.info("SalesAIEngine shutdown")
