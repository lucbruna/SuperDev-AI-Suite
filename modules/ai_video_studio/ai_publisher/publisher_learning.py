"""Publisher Learning — learns from historical publish outcomes (Volume 7)."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class PublisherLearning:
    """Weighted feedback loop over past publish results (no external ML deps)."""

    def __init__(self) -> None:
        self._samples: list[dict] = []
        self._feature_weights: dict[str, float] = {
            "title_score": 1.0,
            "description_score": 1.0,
            "tags_score": 1.0,
            "has_thumbnail": 0.8,
            "posted_in_window": 0.6,
        }

    def record(self, *, outcome: dict) -> dict:
        """Record one publish outcome (metrics + features) and update weights."""
        metrics = outcome.get("metrics", {})
        engagement = (
            metrics.get("likes", 0) * 1.0
            + metrics.get("comments", 0) * 2.0
            + metrics.get("shares", 0) * 3.0
            + metrics.get("views", 0) * 0.1
        )
        features = outcome.get("features", {})
        sample = {"features": features, "engagement": engagement}
        self._samples.append(sample)
        # Simple online update: reinforce features present in above-average outcomes.
        avg = sum(s["engagement"] for s in self._samples) / max(1, len(self._samples))
        for feature, value in features.items():
            if feature in self._feature_weights and value:
                if engagement > avg:
                    self._feature_weights[feature] += 0.05
                else:
                    self._feature_weights[feature] = max(0.1, self._feature_weights[feature] - 0.02)
        return {"recorded": True, "samples": len(self._samples)}

    def predict(self, *, features: dict) -> dict:
        """Predict relative engagement for a feature set using learned weights."""
        score = 0.0
        for feature, value in features.items():
            if feature in self._feature_weights and value:
                score += self._feature_weights[feature] * float(value)
        return {"predicted_score": round(score, 3), "weights": dict(self._feature_weights)}

    def stats(self) -> dict[str, int | float]:
        return {"samples": len(self._samples), "features": len(self._feature_weights)}


_LEARNING: PublisherLearning | None = None


def get_publisher_learning() -> PublisherLearning:
    """Get the module-level singleton learning engine."""
    global _LEARNING
    if _LEARNING is None:
        _LEARNING = PublisherLearning()
    return _LEARNING
