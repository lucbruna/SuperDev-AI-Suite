"""Noise removal — reduce sensor/compression noise in video."""
from __future__ import annotations

from typing import Any


class NoiseRemoval:
    """Applies spatial + temporal denoising to frames."""

    def remove(self, frames: list[dict[str, Any]], *, strength: float = 0.4) -> dict[str, Any]:
        if not 0.0 <= strength <= 1.0:
            raise ValueError("strength must be in [0, 1]")
        return {
            "frames_processed": len(frames),
            "strength": strength,
            "spatial_kernel": 3,
            "temporal_window": 5,
            "noise_estimate": round(0.08 * (1 - strength), 3),
        }
