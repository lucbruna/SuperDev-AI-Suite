"""Edit decision — plans the editing approach."""
from __future__ import annotations

from typing import Any


class EditDecision:
    """Defines the editing style and rhythm."""

    def decide(self, rhythm: str = "energetic") -> dict[str, Any]:
        cuts_per_minute = {"slow": 4, "energetic": 12, "punchy": 20}.get(rhythm, 8)
        return {
            "rhythm": rhythm,
            "cuts_per_minute": cuts_per_minute,
            "transition": "cut" if rhythm != "slow" else "dissolve",
        }


_edit_decision: EditDecision | None = None


def get_edit_decision() -> EditDecision:
    global _edit_decision
    if _edit_decision is None:
        _edit_decision = EditDecision()
    return _edit_decision
