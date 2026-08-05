"""Idle pose — neutral resting gestures."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Gesture:
    """A named body gesture (arm lifts, lean, head motion)."""

    name: str
    arm_left: float = 0.0
    arm_right: float = 0.0
    lean: float = 0.0
    head: str = "neutral"

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "arm_left": self.arm_left,
                "arm_right": self.arm_right, "lean": self.lean, "head": self.head}


IDLE_GESTURES = [
    Gesture("idle_rest", 0.0, 0.0, 0.0, "neutral"),
    Gesture("idle_hands_together", 0.2, 0.2, 0.0, "neutral"),
    Gesture("idle_weight_shift", 0.0, 0.1, -0.1, "neutral"),
]


def gestures() -> list[Gesture]:
    return IDLE_GESTURES
