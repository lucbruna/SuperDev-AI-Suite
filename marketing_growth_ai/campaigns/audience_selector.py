"""
Audience Selector - Selects target audiences
"""

from typing import Any, Dict, List
from uuid import UUID

from marketing_growth_ai.marketing_models import CustomerSegment


class AudienceSelector:
    """Selects target audiences"""

    def __init__(self):
        self._segments: Dict[UUID, CustomerSegment] = {}

    def add_segment(self, segment: CustomerSegment) -> None:
        self._segments[segment.id] = segment

    def select_for_campaign(
        self,
        campaign_objective: str,
        product_category: str,
        budget: float,
    ) -> List[CustomerSegment]:
        scored = []
        for segment in self._segments.values():
            score = self._score_segment(segment, campaign_objective, product_category, budget)
            if score > 0:
                scored.append((score, segment))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [s for _, s in scored[:5]]

    def _score_segment(
        self,
        segment: CustomerSegment,
        objective: str,
        category: str,
        budget: float,
    ) -> float:
        score = 0.0
        score += segment.size * 0.1
        score += segment.engagement_rate * 100
        score += segment.conversion_rate * 1000
        score += segment.average_order_value * 0.01
        return score

    def get_lookalike_audience(self, seed_segment: UUID, size: int = 100000) -> Dict[str, Any]:
        return {"seed": str(seed_segment), "estimated_size": size, "similarity": 0.85}

    def get_retargeting_audience(
        self,
        website_visitors_days: int = 30,
        cart_abandoners: bool = True,
    ) -> Dict[str, Any]:
        return {"type": "retargeting", "visitors_days": website_visitors_days}