"""LinkedIn Optimizer — content optimization for LinkedIn (Volume 7)."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class LinkedInOptimizer:
    """Score LinkedIn content and suggest improvements."""

    def score(self, *, text_length: int = 0, has_question: bool = False, has_media: bool = False, has_hashtags: bool = False) -> dict:
        """Return a 0-100 readiness score with breakdown."""
        score = 0.0
        breakdown = {}
        score += 30.0 if 150 <= text_length <= 3000 else 15.0
        breakdown["length"] = "good" if 150 <= text_length <= 3000 else "needs_work"
        score += 25.0 if has_question else 0.0
        breakdown["question"] = bool(has_question)
        score += 25.0 if has_media else 0.0
        breakdown["media"] = bool(has_media)
        score += 20.0 if has_hashtags else 0.0
        breakdown["hashtags"] = bool(has_hashtags)
        overall = round(min(100.0, score), 1)
        return {"score": overall, "rating": "high" if overall >= 75 else "medium" if overall >= 50 else "low", "breakdown": breakdown}

    def suggest(self, *, text_length: int = 0, has_question: bool = False, has_media: bool = False, has_hashtags: bool = False) -> list[str]:
        """Generate optimization suggestions."""
        suggestions = []
        if not (150 <= text_length <= 3000):
            suggestions.append("Keep the post between 150 and 3000 characters.")
        if not has_question:
            suggestions.append("End with a question to drive comments.")
        if not has_media:
            suggestions.append("Add an image, carousel, or video — media boosts reach.")
        if not has_hashtags:
            suggestions.append("Add 3-5 relevant hashtags.")
        if not suggestions:
            suggestions.append("Content is well optimized for LinkedIn.")
        return suggestions

    def stats(self) -> dict[str, int]:
        return {"criteria": 4}


_OPTIMIZER: LinkedInOptimizer | None = None


def get_linkedin_optimizer() -> LinkedInOptimizer:
    """Get the module-level singleton LinkedIn optimizer."""
    global _OPTIMIZER
    if _OPTIMIZER is None:
        _OPTIMIZER = LinkedInOptimizer()
    return _OPTIMIZER
