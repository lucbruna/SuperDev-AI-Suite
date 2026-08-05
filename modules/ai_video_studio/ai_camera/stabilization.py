"""Stabilization — remove unwanted camera shake from footage."""
from __future__ import annotations

from typing import Any


class Stabilization:
    """Applies translation/rotation smoothing to camera paths."""

    def stabilize_path(self, path: list[dict[str, Any]], *, window: int = 5) -> list[dict[str, Any]]:
        if window < 1:
            raise ValueError("window must be >= 1")
        result: list[dict[str, Any]] = []
        for i, point in enumerate(path):
            positions = [p["position"] for p in path[max(0, i - window) : i + window + 1]]
            smoothed = tuple(
                round(sum(pos[k] for pos in positions) / len(positions), 3) for k in range(3)
            )
            result.append({**point, "position": smoothed, "stabilized": True})
        return result
