"""Body proportions — classic human proportion ratios."""
from __future__ import annotations

from typing import Any


class BodyProportions:
    """Computes human-proportion ratios from height (8-head canon)."""

    def for_height(self, height_cm: int) -> dict[str, Any]:
        head = height_cm / 8.0
        return {
            "head_ratio": head / height_cm,
            "torso_ratio": 0.30,
            "arm_length_ratio": 0.40,
            "leg_length_ratio": 0.48,
            "shoulder_width_ratio": 0.25,
            "head_height_cm": round(head, 1),
        }


_body_proportions: BodyProportions | None = None


def get_body_proportions() -> BodyProportions:
    global _body_proportions
    if _body_proportions is None:
        _body_proportions = BodyProportions()
    return _body_proportions
