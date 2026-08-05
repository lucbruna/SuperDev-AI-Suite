"""Screenwriter optimizer — refines scripts based on review feedback."""
from __future__ import annotations

from typing import Any


class ScreenwriterOptimizer:
    """Optimizes scripts by applying review suggestions."""

    def optimize(self, script: dict[str, Any], review: dict[str, Any]) -> dict[str, Any]:
        script["score"] = review.get("score", 0.0)
        script["issues"] = review.get("issues", [])
        return script

    def trim_to_duration(self, script: dict[str, Any], target: float, wpm: int = 150) -> dict[str, Any]:
        text = script.get("text", "")
        words = len(text.split())
        current = words / wpm * 60
        if current <= target:
            return script
        allowed_words = int(target / 60 * wpm)
        trimmed = " ".join(text.split()[:allowed_words])
        script["text"] = trimmed
        return script


_screenwriter_optimizer: ScreenwriterOptimizer | None = None


def get_screenwriter_optimizer() -> ScreenwriterOptimizer:
    global _screenwriter_optimizer
    if _screenwriter_optimizer is None:
        _screenwriter_optimizer = ScreenwriterOptimizer()
    return _screenwriter_optimizer
