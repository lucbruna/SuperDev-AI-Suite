"""Avatar learning — learn preferred styles, emotions and gestures."""
from __future__ import annotations

from typing import Any


class AvatarLearning:
    """Records feedback and surfaces preferred avatar choices."""

    def __init__(self) -> None:
        self._scores: dict[str, list[float]] = {}

    def record(self, key: str, score: float) -> None:
        if not 0 <= score <= 1:
            raise ValueError("score must be in [0, 1]")
        self._scores.setdefault(key, []).append(score)

    def _best(self, prefix: str) -> str | None:
        best: tuple[str, float] | None = None
        for key, values in self._scores.items():
            if not key.startswith(prefix):
                continue
            avg = sum(values) / len(values)
            if best is None or avg > best[1]:
                best = (key, avg)
        return best

    def preferred(self, prefix: str) -> str | None:
        best = self._best(prefix)
        return best[0].split(":", 1)[1] if best else None

    def report(self, prefix: str | None = None) -> dict[str, Any]:
        return {
            key: {"count": len(v), "average": round(sum(v) / len(v), 3)}
            for key, v in self._scores.items()
            if prefix is None or key.startswith(prefix)
        }

    def reset(self) -> None:
        self._scores.clear()


_avatar_learning: AvatarLearning | None = None


def get_avatar_learning() -> AvatarLearning:
    global _avatar_learning
    if _avatar_learning is None:
        _avatar_learning = AvatarLearning()
    return _avatar_learning
