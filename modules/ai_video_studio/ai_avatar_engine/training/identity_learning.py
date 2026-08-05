"""Identity learning — learns preferred avatar identities over time."""
from __future__ import annotations

from typing import Any


class IdentityLearning:
    """Tracks preference scores per avatar profile id."""

    def __init__(self) -> None:
        self._scores: dict[str, list[float]] = {}

    def record(self, profile_id: str, score: float) -> None:
        if not 0 <= score <= 1:
            raise ValueError("score must be in [0, 1]")
        self._scores.setdefault(profile_id, []).append(score)

    def preferred(self) -> str | None:
        best: tuple[str, float] | None = None
        for pid, scores in self._scores.items():
            avg = sum(scores) / len(scores)
            if best is None or avg > best[1]:
                best = (pid, avg)
        return best[0] if best else None

    def report(self) -> dict[str, Any]:
        return {pid: round(sum(s) / len(s), 3) for pid, s in self._scores.items()}


_identity_learning: IdentityLearning | None = None


def get_identity_learning() -> IdentityLearning:
    global _identity_learning
    if _identity_learning is None:
        _identity_learning = IdentityLearning()
    return _identity_learning
