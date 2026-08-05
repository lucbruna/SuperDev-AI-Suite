"""Camera follow — smooth follow behaviour for targets."""
from __future__ import annotations

from typing import Any


class CameraFollow:
    """Tracks a target with optional offset and damping."""

    def __init__(self, *, offset: tuple[float, float, float] = (0, 1.5, 3.0), damping: float = 0.1) -> None:
        self.offset = offset
        self.damping = damping

    def follow(self, target: tuple[float, float, float]) -> dict[str, Any]:
        return {
            "position": (
                round(target[0] + self.offset[0], 3),
                round(target[1] + self.offset[1], 3),
                round(target[2] + self.offset[2], 3),
            ),
            "target": list(target),
            "damping": self.damping,
        }
