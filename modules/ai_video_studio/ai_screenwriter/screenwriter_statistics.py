"""Screenwriter statistics — aggregates metrics across scripts."""
from __future__ import annotations

from typing import Any


class ScreenwriterStatistics:
    """Computes aggregate statistics over a set of scripts."""

    def summarize(self, scripts: list[dict[str, Any]]) -> dict[str, Any]:
        if not scripts:
            return {"count": 0, "avg_score": 0.0, "avg_words": 0}
        scores = [s.get("score", 0.0) for s in scripts]
        word_counts = [len(s.get("text", "").split()) for s in scripts]
        return {
            "count": len(scripts),
            "avg_score": sum(scores) / len(scores),
            "avg_words": sum(word_counts) / len(word_counts),
            "best_score": max(scores),
        }


_screenwriter_statistics: ScreenwriterStatistics | None = None


def get_screenwriter_statistics() -> ScreenwriterStatistics:
    global _screenwriter_statistics
    if _screenwriter_statistics is None:
        _screenwriter_statistics = ScreenwriterStatistics()
    return _screenwriter_statistics
