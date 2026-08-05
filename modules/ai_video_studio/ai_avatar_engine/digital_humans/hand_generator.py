"""Hand generator — hand geometry and finger-length parameters."""
from __future__ import annotations

from typing import Any


class HandGenerator:
    """Generates hand parameters."""

    def generate(self, *, seed: int | None = None) -> dict[str, Any]:
        return {
            "finger_length_ratio": 0.42 + ((seed or 0) % 4) * 0.02,
            "palm_width_ratio": 0.5,
            "nail_length": 0.3 + ((seed or 0) % 3) * 0.1,
            "thumb_angle": 20 + (seed or 0) % 15,
            "skin_tone_match": True,
        }


_hand_generator: HandGenerator | None = None


def get_hand_generator() -> HandGenerator:
    global _hand_generator
    if _hand_generator is None:
        _hand_generator = HandGenerator()
    return _hand_generator
