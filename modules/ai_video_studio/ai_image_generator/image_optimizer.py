"""Image optimizer — tune image generation parameters."""
from __future__ import annotations

from typing import Any


class ImageOptimizer:
    """Computes sensible generation settings for a target size."""

    def optimize(self, *, size: tuple[int, int] = (1024, 1024), profile: str = "balanced") -> dict[str, Any]:
        width, height = size
        pixels = width * height
        profiles = {
            "speed": {"steps": 20, "guidance": 5.0},
            "balanced": {"steps": 30, "guidance": 7.0},
            "quality": {"steps": 45, "guidance": 9.0},
        }
        if profile not in profiles:
            raise ValueError(f"Unknown profile '{profile}'")
        base = profiles[profile]
        batch_size = 8 if pixels <= 1024 * 1024 else 4 if pixels <= 2048 * 2048 else 1
        return {
            "width": width,
            "height": height,
            "steps": base["steps"],
            "guidance_scale": base["guidance"],
            "batch_size": batch_size,
            "profile": profile,
        }


_image_optimizer: ImageOptimizer | None = None


def get_image_optimizer() -> ImageOptimizer:
    global _image_optimizer
    if _image_optimizer is None:
        _image_optimizer = ImageOptimizer()
    return _image_optimizer
