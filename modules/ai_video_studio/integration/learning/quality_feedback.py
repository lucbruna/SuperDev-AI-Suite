"""Quality Feedback — aggregates user quality ratings."""
from __future__ import annotations

from typing import Any


class QualityFeedback:
    """Tracks quality scores per output type."""

    def __init__(self) -> None:
        self._scores: dict[str, list[float]] = {}

    def submit(self, output_type: str, score: float) -> dict[str, Any]:
        score = max(0.0, min(5.0, float(score)))
        self._scores.setdefault(output_type, []).append(score)
        return {"output_type": output_type, "score": score, "n": len(self._scores[output_type])}

    def summary(self) -> dict[str, Any]:
        return {
            output: {"n": len(v), "avg": round(sum(v) / len(v), 2)}
            for output, v in self._scores.items()
        }


_quality_feedback: QualityFeedback | None = None


def get_quality_feedback() -> QualityFeedback:
    global _quality_feedback
    if _quality_feedback is None:
        _quality_feedback = QualityFeedback()
    return _quality_feedback
