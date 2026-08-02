"""Market rating — per-skill scores and leaderboards."""
from __future__ import annotations
from typing import Any


class MarketRating:
    """Tracks 1..5 ratings per skill and exposes averages."""

    def __init__(self) -> None:
        self._ratings: dict[str, list[int]] = {}

    def rate(self, skill_id: str, score: int, *, rater: str = "anonymous") -> dict[str, Any]:
        score = int(score)
        if not 1 <= score <= 5:
            raise ValueError("score must be between 1 and 5")
        self._ratings.setdefault(skill_id, []).append(score)
        return {
            "skill_id": skill_id,
            "score": score,
            "rater": rater,
            "average": self.average(skill_id),
            "votes": len(self._ratings[skill_id]),
        }

    def average(self, skill_id: str) -> float | None:
        scores = self._ratings.get(skill_id)
        if not scores:
            return None
        return round(sum(scores) / len(scores), 2)

    def votes(self, skill_id: str) -> int:
        return len(self._ratings.get(skill_id, []))

    def top(self, limit: int = 5) -> list[dict[str, Any]]:
        scored = [
            {"skill_id": sid, "average": self.average(sid), "votes": self.votes(sid)}
            for sid in self._ratings
        ]
        scored.sort(key=lambda s: (s["average"] or 0, s["votes"]), reverse=True)
        return scored[:limit]
