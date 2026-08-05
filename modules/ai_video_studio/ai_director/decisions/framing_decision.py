"""Framing decision — determines on-screen framing rules."""
from __future__ import annotations

from typing import Any

FRAMINGS = ["rule_of_thirds", "center", "leading_lines", "symmetry"]


class FramingDecision:
    """Selects framing guidance for a shot."""

    def decide(self, shot: str = "medium") -> dict[str, Any]:
        framing = FRAMINGS[1] if shot in ("closeup", "extreme_closeup") else FRAMINGS[0]
        return {"shot": shot, "framing": framing, "headroom": "one_third"}


_framing_decision: FramingDecision | None = None


def get_framing_decision() -> FramingDecision:
    global _framing_decision
    if _framing_decision is None:
        _framing_decision = FramingDecision()
    return _framing_decision
