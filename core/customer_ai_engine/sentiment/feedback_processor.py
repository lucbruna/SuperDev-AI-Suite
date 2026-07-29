"""
Feedback Processor - Collect, process, and analyze customer feedback.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..customer_context import CustomerContext
from ..customer_events import CustomerEvent, CustomerEventBus, EventType
from ..customer_models import Feedback, SentimentType
from ..customer_config import CustomerConfig

logger = logging.getLogger(__name__)


class FeedbackProcessor:
    def __init__(self, config: CustomerConfig, context: CustomerContext, event_bus: CustomerEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self._feedbacks: List[Feedback] = []

    def submit(self, customer_id: str, rating: int, comment: str, category: str = "") -> Feedback:
        feedback = Feedback(
            id=str(uuid.uuid4()),
            customer_id=customer_id,
            rating=rating,
            comment=comment,
            category=category,
        )
        self._feedbacks.append(feedback)
        logger.info(f"Feedback submitted: {customer_id} rating={rating}")
        return feedback

    def get_by_customer(self, customer_id: str) -> List[Feedback]:
        return [f for f in self._feedbacks if f.customer_id == customer_id]

    def get_by_category(self, category: str) -> List[Feedback]:
        return [f for f in self._feedbacks if f.category == category]

    def get_summary(self) -> Dict[str, Any]:
        if not self._feedbacks:
            return {"total": 0, "average_rating": 0, "categories": {}}
        avg = sum(f.rating for f in self._feedbacks) / len(self._feedbacks)
        categories = {}
        for f in self._feedbacks:
            cat = f.category or "general"
            if cat not in categories:
                categories[cat] = {"count": 0, "total_rating": 0}
            categories[cat]["count"] += 1
            categories[cat]["total_rating"] += f.rating
        for cat in categories:
            categories[cat]["average"] = round(categories[cat]["total_rating"] / categories[cat]["count"], 2)
        return {
            "total": len(self._feedbacks),
            "average_rating": round(avg, 2),
            "categories": categories,
        }
