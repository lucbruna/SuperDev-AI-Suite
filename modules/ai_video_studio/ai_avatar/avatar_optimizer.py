"""Avatar optimizer — quality/speed tradeoffs for presenter renders."""
from __future__ import annotations

from typing import Any


class AvatarOptimizer:
    """Computes render settings for a target quality profile."""

    _PROFILES = {
        "draft": {"fps_scale": 0.5, "substeps": 2, "ik_iterations": 10},
        "high": {"fps_scale": 1.0, "substeps": 6, "ik_iterations": 30},
        "final": {"fps_scale": 1.5, "substeps": 12, "ik_iterations": 60},
    }

    def optimize(self, *, quality: str = "high", fps: int = 24) -> dict[str, Any]:
        if quality not in self._PROFILES:
            raise ValueError(f"Unknown quality '{quality}'")
        profile = self._PROFILES[quality]
        return {
            "quality": quality,
            "fps": max(1, int(fps * profile["fps_scale"])),
            "substeps": profile["substeps"],
            "ik_iterations": profile["ik_iterations"],
        }


_avatar_optimizer: AvatarOptimizer | None = None


def get_avatar_optimizer() -> AvatarOptimizer:
    global _avatar_optimizer
    if _avatar_optimizer is None:
        _avatar_optimizer = AvatarOptimizer()
    return _avatar_optimizer
