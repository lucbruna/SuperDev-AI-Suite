"""Hand tracking — skin-tone blobs in the lower frame (hands region)."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


class HandTracker:
    """Finds skin-colored blobs (hands) via normalized-RGB heuristic."""

    def __call__(self, frame: NDArray[np.floating]) -> list[dict]:
        f = frame.astype(np.float64)
        r, g, b = f[..., 0], f[..., 1], f[..., 2]
        with np.errstate(divide="ignore", invalid="ignore"):
            denom = np.maximum(r + g + b, 1e-6)
            nr, ng = r / denom, g / denom
        mask = (nr > 0.25) & (ng > 0.2) & (np.abs(nr - ng) < 0.12) & (r > 0.3)
        ys, xs = np.where(mask)
        if len(xs) == 0:
            return []
        # Simple connected-component labeling via row clustering
        points = np.stack([ys, xs], axis=1)
        clusters: list[np.ndarray] = []
        while len(points):
            seed = points[0]
            dist = np.abs(points - seed).sum(axis=1)
            members = points[dist < 40]
            clusters.append(members)
            points = points[dist >= 40]
        out = []
        for c in clusters[:4]:
            if len(c) < 20:
                continue
            out.append(
                {
                    "x": float(c[:, 1].mean()),
                    "y": float(c[:, 0].mean()),
                    "w": float(c[:, 1].ptp()),
                    "h": float(c[:, 0].ptp()),
                    "kind": "hand",
                }
            )
        return out
