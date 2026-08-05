"""Avatar optimizer — quality/speed profiles for avatar generation."""
from __future__ import annotations

from typing import Any

_PROFILES = {
    "draft": {"fps_scale": 0.5, "substeps": 2, "mesh_quality": 0.4, "samples": 4},
    "high": {"fps_scale": 1.0, "substeps": 6, "mesh_quality": 0.8, "samples": 16},
    "final": {"fps_scale": 1.5, "substeps": 12, "mesh_quality": 1.0, "samples": 32},
}


class AvatarOptimizer:
    """Computes render settings for a target quality profile."""

    def optimize(self, *, quality: str = "high", fps: int = 24,
                 resolution: str = "1280x720") -> dict[str, Any]:
        if quality not in _PROFILES:
            raise ValueError(f"Unknown quality '{quality}' (draft|high|final)")
        profile = _PROFILES[quality]
        width, height = (int(p) for p in resolution.split("x"))
        return {
            "quality": quality,
            "fps": max(1, int(fps * profile["fps_scale"])),
            "substeps": profile["substeps"],
            "mesh_quality": profile["mesh_quality"],
            "samples": profile["samples"],
            "width": width,
            "height": height,
            "resolution": resolution,
        }


_avatar_optimizer: AvatarOptimizer | None = None


def get_avatar_optimizer() -> AvatarOptimizer:
    global _avatar_optimizer
    if _avatar_optimizer is None:
        _avatar_optimizer = AvatarOptimizer()
    return _avatar_optimizer
