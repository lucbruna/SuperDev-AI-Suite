"""Take decision — selects the best take from a set."""
from __future__ import annotations

from typing import Any


class TakeDecision:
    """Picks the best take by score."""

    def decide(self, takes: list[dict[str, Any]]) -> dict[str, Any]:
        if not takes:
            return {"best": None, "reason": "no takes"}
        best = max(takes, key=lambda take: take.get("score", 0.0))
        return {"best": best.get("id"), "reason": best.get("note", "highest score")}


_take_decision: TakeDecision | None = None


def get_take_decision() -> TakeDecision:
    global _take_decision
    if _take_decision is None:
        _take_decision = TakeDecision()
    return _take_decision
