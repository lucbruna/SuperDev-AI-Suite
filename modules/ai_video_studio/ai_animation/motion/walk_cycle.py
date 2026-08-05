"""Walk cycle — procedural biped walk animation."""
from __future__ import annotations

import math
from typing import Any


class WalkCycle:
    """Generates leg/arm swing curves for a walk cycle."""

    def pose(self, t: float, *, speed: float = 1.0) -> dict[str, Any]:
        phase = t * math.pi * 2 * speed
        return {
            "leg_l_swing": round(math.sin(phase), 4),
            "leg_r_swing": round(math.sin(phase + math.pi), 4),
            "arm_l_swing": round(math.sin(phase + math.pi) * 0.4, 4),
            "arm_r_swing": round(math.sin(phase) * 0.4, 4),
            "bob": round(abs(math.sin(phase)) * 0.02, 4),
        }

    def cycle(self, frames: int) -> list[dict[str, Any]]:
        return [self.pose(i / max(1, frames - 1)) for i in range(frames)]
