"""Finger movements — fine hand/finger gestures."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FingerGesture:
    """A finger-level gesture with per-finger curl parameters."""

    name: str
    thumb: float = 0.0
    index: float = 0.0
    middle: float = 0.0
    ring: float = 0.0
    pinky: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "thumb": self.thumb, "index": self.index,
                "middle": self.middle, "ring": self.ring, "pinky": self.pinky}


FINGER_GESTURES = [
    FingerGesture("finger_point", thumb=0.3, index=1.0),
    FingerGesture("finger_thumbs_up", thumb=1.0),
    FingerGesture("finger_ok", thumb=0.9, index=0.9),
    FingerGesture("finger_peace", index=1.0, middle=1.0),
    FingerGesture("finger_fist", thumb=0.8, index=0.8, middle=0.8, ring=0.8, pinky=0.8),
]


def gestures() -> list[FingerGesture]:
    return FINGER_GESTURES
