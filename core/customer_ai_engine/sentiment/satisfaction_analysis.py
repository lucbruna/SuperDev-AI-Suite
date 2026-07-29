"""
Satisfaction Analysis - Measure customer satisfaction from interactions.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..customer_context import CustomerContext
from ..customer_events import CustomerEventBus
from ..customer_config import CustomerConfig

logger = logging.getLogger(__name__)


class SatisfactionAnalysis:
    def __init__(self, config: CustomerConfig, context: CustomerContext, event_bus: CustomerEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self._ratings: Dict[str, List[int]] = {}

    def add_rating(self, customer_id: str, rating: int) -> None:
        if customer_id not in self._ratings:
            self._ratings[customer_id] = []
        self._ratings[customer_id].append(max(1, min(5, rating)))

    def get_csat(self, customer_id: str) -> float:
        ratings = self._ratings.get(customer_id, [])
        if not ratings:
            return 0.0
        return sum(ratings) / len(ratings)

    def get_average_csat(self) -> float:
        all_ratings = []
        for ratings in self._ratings.values():
            all_ratings.extend(ratings)
        if not all_ratings:
            return 0.0
        return sum(all_ratings) / len(all_ratings)

    def get_nps(self) -> float:
        all_ratings = []
        for ratings in self._ratings.values():
            all_ratings.extend(ratings)
        if not all_ratings:
            return 0.0
        promoters = sum(1 for r in all_ratings if r >= 4)
        detractors = sum(1 for r in all_ratings if r <= 2)
        total = len(all_ratings)
        return ((promoters - detractors) / total) * 100
