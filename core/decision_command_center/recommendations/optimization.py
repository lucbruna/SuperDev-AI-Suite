from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

from ..decision_config import DecisionConfig
from ..decision_models import Recommendation, RecommendationPriority, BusinessArea

logger = logging.getLogger(__name__)


class Optimization:
    def __init__(self, config: DecisionConfig):
        self._config = config

    def optimize_roi(self, recommendations: List[Recommendation], budget: float = 100000.0) -> List[Recommendation]:
        feasible = [r for r in recommendations if r.roi_estimate > 0 and r.effort_hours * 100 <= budget]
        feasible.sort(key=lambda r: r.roi_estimate / max(r.effort_hours, 1), reverse=True)
        return feasible

    def balance_portfolio(self, recommendations: List[Recommendation]) -> Dict[str, Any]:
        by_area: Dict[str, List[Recommendation]] = {}
        for r in recommendations:
            area = r.business_area.value
            if area not in by_area:
                by_area[area] = []
            by_area[area].append(r)
        return {area: len(recs) for area, recs in by_area.items()}

    def resource_allocation(self, recommendations: List[Recommendation], total_hours: int = 1000) -> List[Recommendation]:
        sorted_recs = sorted(recommendations, key=lambda r: r.roi_estimate / max(r.effort_hours, 1), reverse=True)
        allocated = []
        hours_used = 0
        for r in sorted_recs:
            if hours_used + r.effort_hours <= total_hours:
                allocated.append(r)
                hours_used += r.effort_hours
        return allocated
