"""Color decision — chooses color grading direction."""
from __future__ import annotations

from typing import Any

GRADES = {
    "corporate": {"saturation": 0.5, "warmth": 0.2, "contrast": 0.6},
    "cinematic": {"saturation": 0.7, "warmth": 0.4, "contrast": 0.8},
    "vibrant": {"saturation": 1.0, "warmth": 0.3, "contrast": 0.5},
    "minimal": {"saturation": 0.3, "warmth": 0.5, "contrast": 0.4},
}


class ColorDecision:
    """Selects a color grade for the production."""

    def decide(self, style: str = "corporate") -> dict[str, Any]:
        return {"style": style, "grade": GRADES.get(style, GRADES["corporate"])}


_color_decision: ColorDecision | None = None


def get_color_decision() -> ColorDecision:
    global _color_decision
    if _color_decision is None:
        _color_decision = ColorDecision()
    return _color_decision
