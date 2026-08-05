"""Neutral emotion preset."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class EmotionPreset:
    """A named emotional state expressed as animation parameters."""

    name: str
    facial: dict[str, float] = field(default_factory=dict)
    body: dict[str, float] = field(default_factory=dict)
    voice: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "facial": dict(self.facial),
                "body": dict(self.body), "voice": dict(self.voice)}


def preset() -> EmotionPreset:
    """Return the neutral emotion preset."""
    return EmotionPreset(
        name="neutral",
        facial={"smile": 0.0, "brow_raise": 0.0, "brow_frown": 0.0,
                "mouth_open": 0.05, "eye_open": 1.0},
        body={"lean": 0.0, "arm_energy": 0.2, "posture": 0.0},
        voice={"pitch_shift": 0.0, "energy": 0.5},
    )
