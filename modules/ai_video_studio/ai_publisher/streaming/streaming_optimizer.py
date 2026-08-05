"""Streaming Optimizer — live stream readiness scoring (Volume 7)."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class StreamingOptimizer:
    """Score stream readiness and suggest improvements."""

    def score(self, *, has_title: bool = False, has_thumbnail: bool = False, has_schedule: bool = False, chat_moderation: bool = False) -> dict:
        """Return a 0-100 readiness score with breakdown."""
        score = 0.0
        breakdown = {}
        score += 30.0 if has_title else 0.0
        breakdown["title"] = bool(has_title)
        score += 25.0 if has_thumbnail else 0.0
        breakdown["thumbnail"] = bool(has_thumbnail)
        score += 25.0 if has_schedule else 0.0
        breakdown["schedule"] = bool(has_schedule)
        score += 20.0 if chat_moderation else 0.0
        breakdown["chat_moderation"] = bool(chat_moderation)
        overall = round(min(100.0, score), 1)
        return {"score": overall, "rating": "high" if overall >= 75 else "medium" if overall >= 50 else "low", "breakdown": breakdown}

    def suggest(self, *, has_title: bool = False, has_thumbnail: bool = False, has_schedule: bool = False, chat_moderation: bool = False) -> list[str]:
        """Generate optimization suggestions."""
        suggestions = []
        if not has_title:
            suggestions.append("Add a clear, keyword-rich stream title.")
        if not has_thumbnail:
            suggestions.append("Prepare an eye-catching thumbnail.")
        if not has_schedule:
            suggestions.append("Announce a fixed schedule so viewers return.")
        if not chat_moderation:
            suggestions.append("Enable chat moderation before going live.")
        if not suggestions:
            suggestions.append("Stream setup is well optimized.")
        return suggestions

    def stats(self) -> dict[str, int]:
        return {"criteria": 4}


_OPTIMIZER: StreamingOptimizer | None = None


def get_streaming_optimizer() -> StreamingOptimizer:
    """Get the module-level singleton streaming optimizer."""
    global _OPTIMIZER
    if _OPTIMIZER is None:
        _OPTIMIZER = StreamingOptimizer()
    return _OPTIMIZER
