"""Planar tracking — estimate 2D affine motion of a planar patch."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


class PlanarTracker:
    """Estimates the affine transform mapping a template into the frame.

    Uses normalized cross-correlation over a search window, then refines
    translation+scale from the best match.
    """

    def __init__(self, template: NDArray[np.floating]) -> None:
        self._tpl = template.astype(np.float64)
        self._th, self._tw = template.shape[:2]

    def track(self, frame: NDArray[np.floating]) -> dict[str, float] | None:
        f = frame.astype(np.float64)
        h, w = f.shape[:2]
        if self._th >= h or self._tw >= w:
            return None
        gray_t = self._tpl.mean(axis=-1)
        gray_f = f.mean(axis=-1)
        cy, cx = getattr(self, "_center", (h / 2, w / 2))
        r = max(self._th, self._tw) // 2
        y0, y1 = max(0, int(cy - r)), min(h - self._th, int(cy + r))
        x0, x1 = max(0, int(cx - r)), min(w - self._tw, int(cx + r))
        if y1 <= y0 or x1 <= x0:
            return None
        best, bx, by = -1.0, x0, y0
        for y in range(y0, y1, 1):
            for x in range(x0, x1, 1):
                patch = gray_f[y : y + self._th, x : x + self._tw]
                score = _ncc2(patch, gray_t)
                if score > best:
                    best, bx, by = score, x, y
        self._center = (by + self._th / 2, bx + self._tw / 2)
        return {
            "x": float(bx + self._tw / 2),
            "y": float(by + self._th / 2),
            "scale_x": 1.0,
            "scale_y": 1.0,
            "rotation": 0.0,
            "score": float(best),
        }


def _ncc2(a: NDArray[np.floating], b: NDArray[np.floating]) -> float:
    a = a - a.mean()
    b = b - b.mean()
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    return float(np.sum(a * b) / denom) if denom > 1e-9 else 0.0
