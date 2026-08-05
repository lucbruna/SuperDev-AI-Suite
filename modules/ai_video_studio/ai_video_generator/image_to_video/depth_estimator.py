"""Depth estimator — produce a depth map descriptor from an image."""
from __future__ import annotations

from typing import Any


class DepthEstimator:
    """Produces a layered depth model for parallax and animation."""

    def estimate(self, image: dict[str, Any]) -> dict[str, Any]:
        width = image.get("width") or 1280
        height = image.get("height") or 720
        return {
            "ref": image.get("ref"),
            "layers": [
                {"name": "background", "depth": 0.1, "z": 10.0},
                {"name": "midground", "depth": 0.5, "z": 5.0},
                {"name": "foreground", "depth": 0.9, "z": 1.0},
            ],
            "map_resolution": [width, height],
        }

    def add_layer(self, depth: dict[str, Any], name: str, depth_value: float, z: float) -> None:
        depth["layers"].append({"name": name, "depth": depth_value, "z": z})
