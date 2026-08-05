"""X Optimizer — content optimization for X (Volume 7)."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class XOptimizer:
    """Score X content and suggest improvements."""

    def score(self, *, text_length: int = 0, has_hashtags: bool = False, has_media: bool = False, has_cta: bool = False) -> dict:
        """Return a 0-100 readiness score with breakdown."""
        score = 0.0
        breakdown = {}
        score += 35.0 if 20 <= text_length <= 280 else 15.0
        breakdown["length"] = "good" if 20 <= text_length <= 280 else "needs_work"
        score += 25.0 if has_hashtags else 0.0
        breakdown["hashtags"] = bool(has_hashtags)
        score += 20.0 if has_media else 0.0
        breakdown["media"] = bool(has_media)
        score += 20.0 if has_cta else 0.0
        breakdown["cta"] = bool(has_cta)
        overall = round(min(100.0, score), 1)
        return {"score": overall, "rating": "high" if overall >= 75 else "medium" if overall >= 50 else "low", "breakdown": breakdown}

    def suggest(self, *, text_length: int = 0, has_hashtags: bool = False, has_media: bool = False, has_cta: bool = False) -> list[str]:
        """Generate optimization suggestions."""
        suggestions = []
        if not (20 <= text_length <= 280):
            suggestions.append("Keep the post between 20 and 280 characters.")
        if not has_hashtags:
            suggestions.append("Add 1-3 relevant hashtags.")
        if not has_media:
            suggestions.append("Add an image or video — media boosts engagement.")
        if not has_cta:
            suggestions.append("Add a call to action (retweet, reply, or link).")
        if not suggestions:
            suggestions.append("Content is well optimized for X.")
        return suggestions

    def stats(self) -> dict[str, int]:
        return {"criteria": 4}


_OPTIMIZER: XOptimizer | None = None


def get_x_optimizer() -> XOptimizer:
    """Get the module-level singleton X optimizer."""
    global _OPTIMIZER
    if _OPTIMIZER is None:
        _OPTIMIZER = XOptimizer()
    return _OPTIMIZER
