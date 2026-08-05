"""Lens decision — recommends lenses per shot type."""
from __future__ import annotations

from typing import Any

LENSES = {"wide": "24mm", "medium": "35mm", "closeup": "50mm", "extreme_closeup": "85mm", "insert": "macro"}


class LensDecision:
    """Recommends a lens for a given shot."""

    def decide(self, shot: str = "medium") -> dict[str, Any]:
        return {"shot": shot, "lens": LENSES.get(shot, "35mm")}


_lens_decision: LensDecision | None = None


def get_lens_decision() -> LensDecision:
    global _lens_decision
    if _lens_decision is None:
        _lens_decision = LensDecision()
    return _lens_decision
