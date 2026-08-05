"""Inverse kinematics — solve limb poses for target positions."""
from __future__ import annotations

import math
from typing import Any


class InverseKinematics:
    """2-segment IK solver for limbs (e.g. arm: shoulder→elbow→hand)."""

    def solve(
        self,
        *,
        origin: tuple[float, float],
        target: tuple[float, float],
        length_a: float,
        length_b: float,
    ) -> dict[str, Any]:
        dx = target[0] - origin[0]
        dy = target[1] - origin[1]
        dist = math.hypot(dx, dy)
        max_reach = length_a + length_b
        if dist > max_reach:
            # Clamp target to maximum reach.
            scale = max_reach / dist
            target = (origin[0] + dx * scale, origin[1] + dy * scale)
            dist = max_reach
        if dist == 0:
            return {"solved": False, "reason": "origin == target"}
        cos_angle = (length_a**2 + dist**2 - length_b**2) / (2 * length_a * dist)
        cos_angle = max(-1.0, min(1.0, cos_angle))
        angle = math.acos(cos_angle)
        base_angle = math.atan2(dy, dx)
        joint = (
            origin[0] + length_a * math.cos(base_angle + angle),
            origin[1] + length_a * math.sin(base_angle + angle),
        )
        return {
            "solved": True,
            "joint": joint,
            "end": (target[0], target[1]),
            "angle_a": base_angle + angle,
            "reachable": dist <= max_reach + 1e-6,
        }
