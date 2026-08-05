"""Pose optimizer — smooth and regularise skeleton poses."""
from __future__ import annotations

from typing import Any


class PoseOptimizer:
    """Blends and clamps pose values for natural motion."""

    def smooth(self, a: dict[str, Any], b: dict[str, Any], alpha: float) -> dict[str, Any]:
        if not 0 <= alpha <= 1:
            raise ValueError("alpha must be in [0, 1]")
        result: dict[str, Any] = {}
        for bone, va in a.items():
            vb = b.get(bone, va)
            if isinstance(va, dict) and isinstance(vb, dict):
                result[bone] = {
                    k: va.get(k, 0) + (vb.get(k, 0) - va.get(k, 0)) * alpha for k in set(va) | set(vb)
                }
            elif isinstance(va, (int, float)) and isinstance(vb, (int, float)):
                result[bone] = va + (vb - va) * alpha
            else:
                result[bone] = va
        return result

    def clamp(self, pose: dict[str, Any], *, limits: dict[str, tuple[float, float]] | None = None) -> dict[str, Any]:
        limits = limits or {}
        result = dict(pose)
        for bone, value in pose.items():
            if bone in limits and isinstance(value, (int, float)):
                low, high = limits[bone]
                result[bone] = max(low, min(high, value))
        return result
