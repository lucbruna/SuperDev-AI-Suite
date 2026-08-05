"""Thumbnail Optimizer — scores and improves social thumbnails (Volume 7)."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class ThumbnailOptimizer:
    """Score thumbnails on composition heuristics and suggest improvements."""

    @staticmethod
    def score(*, features: dict) -> dict:
        """Score a thumbnail from extracted features (0-100)."""
        score = 0.0
        if features.get("has_face"):
            score += 30.0
        if features.get("contrast", 0) >= 0.35:
            score += 20.0
        if features.get("brightness", 0.5) >= 0.4:
            score += 15.0
        if features.get("text_coverage", 0) and 0.05 <= features.get("text_coverage", 0) <= 0.35:
            score += 20.0
        if features.get("colorful"):
            score += 15.0
        overall = round(min(100.0, score), 1)
        return {
            "score": overall,
            "rating": "high" if overall >= 80 else "medium" if overall >= 55 else "low",
            "breakdown": {
                "face": features.get("has_face", False),
                "contrast": features.get("contrast", 0),
                "text_coverage": features.get("text_coverage", 0),
            },
        }

    @staticmethod
    def suggest(*, features: dict) -> list[str]:
        """Return improvement suggestions based on missing features."""
        suggestions = []
        if not features.get("has_face"):
            suggestions.append("Include a face close-up for emotional connection.")
        if features.get("contrast", 0) < 0.35:
            suggestions.append("Increase contrast between subject and background.")
        if features.get("text_coverage", 0) > 0.35:
            suggestions.append("Reduce text area — keep overlay under a third of the frame.")
        if not features.get("colorful"):
            suggestions.append("Add a bold accent color to pop in the feed.")
        if not suggestions:
            suggestions.append("Thumbnail already well optimized.")
        return suggestions

    def stats(self) -> dict[str, int]:
        return {"criteria": 5}


_OPTIMIZER: ThumbnailOptimizer | None = None


def get_thumbnail_optimizer() -> ThumbnailOptimizer:
    """Get the module-level singleton thumbnail optimizer."""
    global _OPTIMIZER
    if _OPTIMIZER is None:
        _OPTIMIZER = ThumbnailOptimizer()
    return _OPTIMIZER
