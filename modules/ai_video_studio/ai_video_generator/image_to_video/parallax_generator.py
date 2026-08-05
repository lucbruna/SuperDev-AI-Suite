"""Parallax generator — create parallax layers from depth data."""
from __future__ import annotations

from typing import Any


class ParallaxGenerator:
    """Splits an image into parallax planes for depth-based motion."""

    def generate(self, depth: dict[str, Any]) -> dict[str, Any]:
        planes = []
        for i, layer in enumerate(depth.get("layers", [])):
            planes.append(
                {
                    "plane": i,
                    "name": layer["name"],
                    "z": layer["z"],
                    "depth": layer["depth"],
                    "shift_per_frame": round((1.0 - layer["depth"]) * 0.4, 3),
                }
            )
        return {"planes": planes, "total": len(planes)}

    def shift(self, plane: dict[str, Any], frame_index: int) -> float:
        return round(plane["shift_per_frame"] * frame_index, 3)
