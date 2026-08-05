"""Pacing analyzer — evaluates narrative rhythm of a script."""
from __future__ import annotations

from typing import Any


class PacingAnalyzer:
    """Analyzes script pacing by section length."""

    def analyze(self, script: dict[str, Any]) -> dict[str, Any]:
        text = script.get("text", "")
        words = len(text.split())
        pace = "balanced"
        if words < 60:
            pace = "fast"
        elif words > 600:
            pace = "slow"
        return {
            "pace": pace,
            "words": words,
            "recommendation": "Keep intro under 15% and outro under 10% of total words.",
        }


_pacing_analyzer: PacingAnalyzer | None = None


def get_pacing_analyzer() -> PacingAnalyzer:
    global _pacing_analyzer
    if _pacing_analyzer is None:
        _pacing_analyzer = PacingAnalyzer()
    return _pacing_analyzer
