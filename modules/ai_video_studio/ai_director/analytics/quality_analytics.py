"""Quality analytics — tracks quality scores across productions."""
from __future__ import annotations



class QualityAnalytics:
    """Aggregates quality scores."""

    def __init__(self) -> None:
        self._scores: list[float] = []

    def record(self, score: float) -> None:
        self._scores.append(score)

    def average(self) -> float:
        if not self._scores:
            return 0.0
        return round(sum(self._scores) / len(self._scores), 3)


_quality_analytics: QualityAnalytics | None = None


def get_quality_analytics() -> QualityAnalytics:
    global _quality_analytics
    if _quality_analytics is None:
        _quality_analytics = QualityAnalytics()
    return _quality_analytics
