"""Animation optimizer — tune animation quality/speed tradeoffs."""
from __future__ import annotations

from typing import Any


class AnimationOptimizer:
    """Computes animation settings for a target quality profile."""

    def optimize(
        self,
        *,
        quality: str = "high",
        fps: int = 24,
        skeleton_solver: str = "fk",
    ) -> dict[str, Any]:
        profiles = {
            "draft": {"substeps": 2, "ik_iterations": 10, "fps_scale": 0.5},
            "high": {"substeps": 6, "ik_iterations": 30, "fps_scale": 1.0},
            "final": {"substeps": 12, "ik_iterations": 60, "fps_scale": 1.5},
        }
        if quality not in profiles:
            raise ValueError(f"Unknown quality '{quality}'")
        profile = profiles[quality]
        return {
            "quality": quality,
            "fps": max(1, int(fps * profile["fps_scale"])),
            "substeps": profile["substeps"],
            "ik_iterations": profile["ik_iterations"],
            "skeleton_solver": skeleton_solver,
        }


_animation_optimizer: AnimationOptimizer | None = None


def get_animation_optimizer() -> AnimationOptimizer:
    global _animation_optimizer
    if _animation_optimizer is None:
        _animation_optimizer = AnimationOptimizer()
    return _animation_optimizer
