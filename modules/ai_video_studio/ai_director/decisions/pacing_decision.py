"""Pacing decision — tunes narrative tempo across sections."""
from __future__ import annotations

from typing import Any


class PacingDecision:
    """Assigns pacing per script section."""

    def decide(self, sections: list[str] | None = None) -> dict[str, Any]:
        names = sections or ["intro", "body", "outro"]
        pacing = {"intro": "quick", "body": "steady", "outro": "quick"}
        return {section: pacing.get(section, "steady") for section in names}


_pacing_decision: PacingDecision | None = None


def get_pacing_decision() -> PacingDecision:
    global _pacing_decision
    if _pacing_decision is None:
        _pacing_decision = PacingDecision()
    return _pacing_decision
