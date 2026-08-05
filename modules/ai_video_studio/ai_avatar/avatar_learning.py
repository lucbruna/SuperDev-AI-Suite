"""Avatar learning — learn preferred actors, emotions and gestures."""
from __future__ import annotations

from typing import Any


class AvatarLearning:
    """Records feedback and surfaces preferred avatar choices."""

    def __init__(self) -> None:
        self._actor_scores: dict[str, list[float]] = {}
        self._emotion_scores: dict[str, list[float]] = {}
        self._gesture_scores: dict[str, list[float]] = {}

    def record(self, *, actor_id: str | None = None, emotion: str | None = None,
               gesture: str | None = None, score: float) -> None:
        if not 0 <= score <= 1:
            raise ValueError("score must be in [0, 1]")
        if actor_id:
            self._actor_scores.setdefault(actor_id, []).append(score)
        if emotion:
            self._emotion_scores.setdefault(emotion, []).append(score)
        if gesture:
            self._gesture_scores.setdefault(gesture, []).append(score)

    @staticmethod
    def _best(scores: dict[str, list[float]]) -> str | None:
        best: tuple[str, float] | None = None
        for key, values in scores.items():
            avg = sum(values) / len(values)
            if best is None or avg > best[1]:
                best = (key, avg)
        return best[0] if best else None

    def preferred_actor(self) -> str | None:
        return self._best(self._actor_scores)

    def preferred_emotion(self) -> str | None:
        return self._best(self._emotion_scores)

    def preferred_gesture(self) -> str | None:
        return self._best(self._gesture_scores)

    def report(self) -> dict[str, Any]:
        return {
            "actors": {k: round(sum(v) / len(v), 3) for k, v in self._actor_scores.items()},
            "emotions": {k: round(sum(v) / len(v), 3) for k, v in self._emotion_scores.items()},
            "gestures": {k: round(sum(v) / len(v), 3) for k, v in self._gesture_scores.items()},
        }


_avatar_learning: AvatarLearning | None = None


def get_avatar_learning() -> AvatarLearning:
    global _avatar_learning
    if _avatar_learning is None:
        _avatar_learning = AvatarLearning()
    return _avatar_learning
