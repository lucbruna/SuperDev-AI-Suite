"""Engagement Predictor — forecasts engagement from content features (Volume 7)."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

_WEIGHTS = {
    "has_face": 0.9,
    "title_score": 0.7,
    "posted_in_window": 0.6,
    "caption_length_ok": 0.4,
    "has_cta": 0.5,
    "quality": 0.8,
}


class EngagementPredictor:
    """Weighted prediction of relative engagement for a post."""

    def predict(self, *, features: dict) -> dict:
        """Return an engagement score (0-1) and qualitative band."""
        score = 0.0
        total_weight = 0.0
        for feature, weight in _WEIGHTS.items():
            value = features.get(feature)
            if value is None:
                continue
            if isinstance(value, bool):
                value = 1.0 if value else 0.0
            if feature == "quality" and isinstance(value, (int, float)):
                value = min(1.0, value / 100.0)
            if isinstance(value, (int, float)):
                score += weight * max(0.0, min(1.0, value))
                total_weight += weight
        normalized = score / total_weight if total_weight else 0.0
        band = "high" if normalized >= 0.75 else "medium" if normalized >= 0.45 else "low"
        return {"score": round(normalized, 3), "band": band}

    def stats(self) -> dict[str, int]:
        return {"features": len(_WEIGHTS)}


_PREDICTOR: EngagementPredictor | None = None


def get_engagement_predictor() -> EngagementPredictor:
    """Get the module-level singleton engagement predictor."""
    global _PREDICTOR
    if _PREDICTOR is None:
        _PREDICTOR = EngagementPredictor()
    return _PREDICTOR
