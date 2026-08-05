"""Shot learning — learns effective shot choices from outcomes."""
from __future__ import annotations



class ShotLearning:
    """Tracks shot effectiveness by type."""

    def __init__(self) -> None:
        self._scores: dict[str, list[float]] = {}

    def record(self, shot: str, score: float) -> None:
        self._scores.setdefault(shot, []).append(score)

    def best(self) -> str:
        if not self._scores:
            return "medium"
        averages = {shot: sum(v) / len(v) for shot, v in self._scores.items()}
        return max(averages, key=lambda shot: averages[shot])


_shot_learning: ShotLearning | None = None


def get_shot_learning() -> ShotLearning:
    global _shot_learning
    if _shot_learning is None:
        _shot_learning = ShotLearning()
    return _shot_learning
