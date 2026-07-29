"""
Conversion Predictor - Predict customer purchase probability.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..customer_context import CustomerContext
from ..customer_events import CustomerEventBus
from ..customer_config import CustomerConfig

logger = logging.getLogger(__name__)


class ConversionPredictor:
    def __init__(self, config: CustomerConfig, context: CustomerContext, event_bus: CustomerEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus

    def predict(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        score = 0.0
        factors = []
        interactions = customer_data.get("interactions", 0)
        if interactions > 10:
            score += 0.3
            factors.append("high_engagement")
        elif interactions > 5:
            score += 0.15
            factors.append("medium_engagement")
        cart_value = customer_data.get("cart_value", 0)
        if cart_value > 1000:
            score += 0.25
            factors.append("high_cart_value")
        elif cart_value > 200:
            score += 0.15
            factors.append("medium_cart_value")
        elif cart_value > 0:
            score += 0.05
            factors.append("low_cart_value")
        page_depth = customer_data.get("page_depth", 0)
        if page_depth > 10:
            score += 0.2
            factors.append("deep_browsing")
        returning = customer_data.get("returning_visitor", False)
        if returning:
            score += 0.15
            factors.append("returning_visitor")
        if customer_data.get("has_consulted", False):
            score += 0.1
            factors.append("consulted_support")
        return {
            "probability": round(min(score, 1.0), 3),
            "factors": factors,
            "segment": "high" if score >= 0.7 else "medium" if score >= 0.4 else "low",
            "expected_value": round(score * customer_data.get("cart_value", 0), 2),
        }

    def predict_batch(self, customers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [self.predict(c) for c in customers]
