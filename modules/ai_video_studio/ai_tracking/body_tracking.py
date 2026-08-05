"""Body tracking — silhouette centroid + smoothed trajectory."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


class BodyTracker:
    """Tracks the centroid of a moving silhouette (person-shaped blob)."""

    def __init__(self, alpha: float = 0.6) -> None:
        self._alpha = alpha
        self._smoothed: tuple[float, float] | None = None

    def __call__(self, frame: NDArray[np.floating]) -> list[dict]:
        f = frame.astype(np.float64)
        # Foreground = strong deviation from mean (simple background diff proxy)
        luma = f.mean(axis=-1)
        dev = np.abs(luma - luma.mean()) > luma.std() * 1.1
        ys, xs = np.where(dev)
        if len(xs) == 0:
            return []
        cx, cy = float(xs.mean()), float(ys.mean())
        if self._smoothed is not None:
            cx = self._alpha * cx + (1 - self._alpha) * self._smoothed[0]
            cy = self._alpha * cy + (1 - self._alpha) * self._smoothed[1]
        self._smoothed = (cx, cy)
        return [{"x": cx, "y": cy, "kind": "body", "score": 0.8}]
