from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..decision_config import DecisionConfig
from ..decision_models import Recommendation, RecommendationPriority

logger = logging.getLogger(__name__)


class PriorityManager:
    def __init__(self, config: DecisionConfig):
        self._config = config

    def score(self, recommendation: Recommendation) -> float:
        priority_weights = {
            RecommendationPriority.CRITICAL: 100,
            RecommendationPriority.HIGH: 70,
            RecommendationPriority.MEDIUM: 40,
            RecommendationPriority.LOW: 10,
        }
        base = priority_weights.get(recommendation.priority, 0)
        roi_score = min(recommendation.roi_estimate / 10000, 50)
        effort_score = max(0, 50 - recommendation.effort_hours / 10)
        return base + roi_score + effort_score

    def rank(self, recommendations: List[Recommendation]) -> List[Recommendation]:
        scored = [(r, self.score(r)) for r in recommendations]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [r for r, _ in scored]

    def get_top(self, recommendations: List[Recommendation], n: int = 5) -> List[Recommendation]:
        return self.rank(recommendations)[:n]
