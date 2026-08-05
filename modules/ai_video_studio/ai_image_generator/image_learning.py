"""Image learning — learn preferred styles from user feedback."""
from __future__ import annotations

from typing import Any


class ImageLearning:
    """Tracks ratings and adapts default style preferences."""

    def __init__(self) -> None:
        self._ratings: dict[str, list[float]] = {}

    def rate(self, style: str, score: float) -> None:
        if not 0 <= score <= 1:
            raise ValueError("score must be in [0, 1]")
        self._ratings.setdefault(style, []).append(score)

    def preferred_style(self) -> str | None:
        best: tuple[str, float] | None = None
        for style, scores in self._ratings.items():
            avg = sum(scores) / len(scores)
            if best is None or avg > best[1]:
                best = (style, avg)
        return best[0] if best else None

    def average_for(self, style: str) -> float | None:
        scores = self._ratings.get(style)
        return sum(scores) / len(scores) if scores else None

    def report(self) -> dict[str, Any]:
        return {
            style: {"ratings": len(scores), "average": round(sum(scores) / len(scores), 3)}
            for style, scores in self._ratings.items()
        }


_image_learning: ImageLearning | None = None


def get_image_learning() -> ImageLearning:
    global _image_learning
    if _image_learning is None:
        _image_learning = ImageLearning()
    return _image_learning
