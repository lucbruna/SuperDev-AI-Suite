"""Vehicle tracking — clusters strong edges into vehicle-like regions."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


class VehicleTracker:
    """Detects boxy high-contrast regions (vehicles) in a frame."""

    def __call__(self, frame: NDArray[np.floating]) -> list[dict]:
        f = frame.astype(np.float64)
        luma = f.mean(axis=-1)
        # High-frequency edge density
        dx = np.abs(np.diff(luma, axis=1))
        dy = np.abs(np.diff(luma, axis=0))
        edge = np.zeros_like(luma)
        edge[:, 1:] += dx
        edge[1:, :] += dy
        strong = edge > np.percentile(edge, 90)
        ys, xs = np.where(strong)
        if len(xs) < 50:
            return []
        # Coarse grid clustering (2x2 bins) then merge
        h, w = luma.shape
        out = []
        for by in range(0, h, max(1, h // 8)):
            for bx in range(0, w, max(1, w // 8)):
                sel = (xs >= bx) & (xs < bx + max(1, w // 8)) & (ys >= by) & (ys < by + max(1, h // 8))
                if sel.sum() < 40:
                    continue
                out.append(
                    {
                        "x": float(xs[sel].mean()),
                        "y": float(ys[sel].mean()),
                        "w": float(xs[sel].ptp()),
                        "h": float(ys[sel].ptp()),
                        "kind": "vehicle",
                    }
                )
        return out[:8]
