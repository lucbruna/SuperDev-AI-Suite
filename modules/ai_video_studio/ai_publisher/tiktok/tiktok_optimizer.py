"""TikTok Optimizer — content optimization for TikTok (Volume 7)."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class TikTokOptimizer:
    """Score TikTok content and suggest improvements."""

    def score(self, *, caption_length: int = 0, has_hook: bool = False, has_cta: bool = False, has_hashtags: bool = False, hook_strength: float = 0.5) -> dict:
        """Return a 0-100 readiness score with breakdown."""
        score = 0.0
        breakdown = {}
        score += 25.0 if 30 <= caption_length <= 150 else 10.0
        breakdown["caption"] = "good" if 30 <= caption_length <= 150 else "needs_work"
        score += 25.0 if has_hook else 0.0
        breakdown["hook"] = bool(has_hook)
        score += 20.0 if has_cta else 0.0
        breakdown["cta"] = bool(has_cta)
        score += 20.0 if has_hashtags else 0.0
        breakdown["hashtags"] = bool(has_hashtags)
        score += min(10.0, hook_strength * 20.0)
        breakdown["hook_strength"] = hook_strength
        overall = round(min(100.0, score), 1)
        return {"score": overall, "rating": "high" if overall >= 75 else "medium" if overall >= 50 else "low", "breakdown": breakdown}

    def suggest(self, *, caption_length: int = 0, has_hook: bool = False, has_cta: bool = False, has_hashtags: bool = False) -> list[str]:
        """Generate optimization suggestions."""
        suggestions = []
        if not (30 <= caption_length <= 150):
            suggestions.append("Keep the caption between 30 and 150 characters.")
        if not has_hook:
            suggestions.append("Open with a strong hook in the first 2 seconds.")
        if not has_cta:
            suggestions.append("Add a call to action (follow, comment, share).")
        if not has_hashtags:
            suggestions.append("Add 3-8 relevant hashtags including #fyp.")
        if not suggestions:
            suggestions.append("Content is well optimized for TikTok.")
        return suggestions

    def stats(self) -> dict[str, int]:
        return {"criteria": 5}


_OPTIMIZER: TikTokOptimizer | None = None


def get_tiktok_optimizer() -> TikTokOptimizer:
    """Get the module-level singleton TikTok optimizer."""
    global _OPTIMIZER
    if _OPTIMIZER is None:
        _OPTIMIZER = TikTokOptimizer()
    return _OPTIMIZER
