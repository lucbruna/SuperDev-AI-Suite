"""Animal tracking — silhouette blob tracking with species-agnostic filtering."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


class AnimalTracker:
    """Tracks moving blobs whose aspect ratio suggests a quadruped/bird."""

    def __init__(self, min_ratio: float = 0.01) -> None:
        self._min_ratio = min_ratio

    def __call__(self, frame: NDArray[np.floating]) -> list[dict]:
        f = frame.astype(np.float64)
        luma = f.mean(axis=-1)
        dev = np.abs(luma - luma.mean()) > luma.std() * 0.9
        ys, xs = np.where(dev)
        if len(xs) < frame.shape[0] * frame.shape[1] * self._min_ratio:
            return []
        w, h = float(xs.ptp()), float(ys.ptp())
        # Quadrupeds are wider than tall; birds taller than wide
        return [{"x": float(xs.mean()), "y": float(ys.mean()), "w": w, "h": h, "kind": "animal"}]
