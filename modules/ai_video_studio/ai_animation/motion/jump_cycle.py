"""Jump cycle — procedural jump with anticipation and landing."""
from __future__ import annotations

from typing import Any


class JumpCycle:
    """Three-phase jump: crouch, airborne arc, landing squash."""

    def pose(self, t: float) -> dict[str, Any]:
        if t < 0.2:
            # Crouch anticipation.
            return {"phase": "crouch", "height": round(-0.05 * (t / 0.2), 4), "squash": 0.9}
        if t < 0.75:
            arc_t = (t - 0.2) / 0.55
            height = 4 * arc_t * (1 - arc_t)  # parabola peak at 0.5
            return {"phase": "air", "height": round(height, 4), "squash": 1.0}
        land_t = (t - 0.75) / 0.25
        return {"phase": "land", "height": round(-0.04 * land_t, 4), "squash": round(1.0 - 0.2 * land_t, 4)}

    def cycle(self, frames: int) -> list[dict[str, Any]]:
        return [self.pose(i / max(1, frames - 1)) for i in range(frames)]
