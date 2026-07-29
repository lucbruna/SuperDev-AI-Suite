"""
Ad Analyzer - Analyzes ad performance
"""

from typing import Any, Dict, List
from uuid import UUID


class AdAnalyzer:
    """Analyzes ad performance"""

    def __init__(self, engine):
        self.engine = engine

    async def analyze_creative(self, creative: Dict) -> Dict[str, Any]:
        score = 0.0
        feedback = []

        if creative.get("headline"):
            score += 20
        else:
            feedback.append("Missing headline")

        if creative.get("description"):
            score += 15
        else:
            feedback.append("Missing description")

        if creative.get("image_url") or creative.get("video_url"):
            score += 25
        else:
            feedback.append("Missing visual content")

        if creative.get("cta"):
            score += 15
        else:
            feedback.append("Missing call to action")

        if creative.get("brand_name"):
            score += 10
        else:
            feedback.append("Missing brand name")

        if creative.get("offer"):
            score += 15

        return {"score": score, "feedback": feedback, "grade": self._grade(score)}

    def _grade(self, score: float) -> str:
        if score >= 90:
            return "A"
        elif score >= 75:
            return "B"
        elif score >= 60:
            return "C"
        else:
            return "D"

    async def analyze_audience_overlap(
        self,
        campaign_ids: List[UUID],
    ) -> Dict[str, Any]:
        return {"overlap": 0.0, "campaigns": []}

    async def diagnose_performance(self, campaign_id: UUID) -> Dict[str, Any]:
        return {
            "campaign_id": str(campaign_id),
            "issues": [],
            "recommendations": [],
        }