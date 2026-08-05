"""Shot decision — decides shot type for each beat."""
from __future__ import annotations

from typing import Any

SHOT_TYPES = ["wide", "medium", "closeup", "extreme_closeup", "insert"]


class ShotDecision:
    """Selects a shot type based on beat emphasis."""

    def decide(self, emphasis: str = "context") -> dict[str, Any]:
        mapping = {
            "context": "wide",
            "action": "medium",
            "emotion": "closeup",
            "detail": "insert",
        }
        shot = mapping.get(emphasis, SHOT_TYPES[1])
        return {"emphasis": emphasis, "shot": shot}


_shot_decision: ShotDecision | None = None


def get_shot_decision() -> ShotDecision:
    global _shot_decision
    if _shot_decision is None:
        _shot_decision = ShotDecision()
    return _shot_decision
