"""Run cycle — procedural run animation with airborne phase."""
from __future__ import annotations

import math
from typing import Any


class RunCycle:
    """Generates a run cycle with contact and airborne phases."""

    def pose(self, t: float) -> dict[str, Any]:
        phase = t * math.pi * 2
        airborne = abs(math.sin(phase)) > 0.75
        return {
            "leg_l_swing": round(math.sin(phase) * 1.2, 4),
            "leg_r_swing": round(math.sin(phase + math.pi) * 1.2, 4),
            "arm_l_swing": round(math.sin(phase + math.pi) * 0.9, 4),
            "arm_r_swing": round(math.sin(phase) * 0.9, 4),
            "body_lean": round(0.35 + 0.05 * math.cos(phase), 4),
            "airborne": airborne,
        }

    def cycle(self, frames: int) -> list[dict[str, Any]]:
        return [self.pose(i / max(1, frames - 1)) for i in range(frames)]
