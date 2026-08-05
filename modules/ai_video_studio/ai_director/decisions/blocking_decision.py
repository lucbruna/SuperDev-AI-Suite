"""Blocking decision — plans actor/staging movement per scene."""
from __future__ import annotations

from typing import Any


class BlockingDecision:
    """Defines on-camera staging."""

    def decide(self, participants: int = 1) -> dict[str, Any]:
        if participants <= 1:
            block = "subject centered, minimal movement"
        elif participants == 2:
            block = "over-shoulder two-shot, facing each other"
        else:
            block = "group staged in triangle formation"
        return {"participants": participants, "blocking": block}


_blocking_decision: BlockingDecision | None = None


def get_blocking_decision() -> BlockingDecision:
    global _blocking_decision
    if _blocking_decision is None:
        _blocking_decision = BlockingDecision()
    return _blocking_decision
