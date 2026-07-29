from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from .decision_models import Insight, InsightType, AlertSeverity, BusinessArea

logger = logging.getLogger(__name__)


class InsightManager:
    def __init__(self):
        self._insights: Dict[str, Insight] = {}
        self._max_insights = 1000

    def create_insight(
        self,
        title: str,
        description: str,
        insight_type: InsightType = InsightType.TREND,
        severity: AlertSeverity = AlertSeverity.INFO,
        business_area: BusinessArea = BusinessArea.STRATEGY,
        confidence: float = 0.0,
    ) -> Insight:
        insight = Insight(
            id=str(uuid.uuid4()),
            title=title,
            description=description,
            insight_type=insight_type,
            severity=severity,
            business_area=business_area,
            confidence=confidence,
        )
        self._insights[insight.id] = insight
        self._trim()
        return insight

    def get_insight(self, insight_id: str) -> Optional[Insight]:
        return self._insights.get(insight_id)

    def acknowledge(self, insight_id: str) -> bool:
        insight = self._insights.get(insight_id)
        if not insight:
            return False
        insight.acknowledged = True
        return True

    def get_by_type(self, insight_type: InsightType) -> List[Insight]:
        return [i for i in self._insights.values() if i.insight_type == insight_type]

    def get_by_area(self, area: BusinessArea) -> List[Insight]:
        return [i for i in self._insights.values() if i.business_area == area]

    def get_active(self) -> List[Insight]:
        return [i for i in self._insights.values() if not i.acknowledged]

    def get_all(self) -> List[Insight]:
        return list(self._insights.values())

    def get_high_impact(self, min_score: float = 70.0) -> List[Insight]:
        return [i for i in self._insights.values() if i.impact_score >= min_score]

    def _trim(self) -> None:
        if len(self._insights) > self._max_insights:
            sorted_ids = sorted(self._insights.keys(), key=lambda k: self._insights[k].created_at)
            for old_id in sorted_ids[:len(self._insights) - self._max_insights]:
                del self._insights[old_id]

    def clear(self) -> None:
        self._insights.clear()
