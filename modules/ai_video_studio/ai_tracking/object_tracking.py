"""Template tracker — locate a template patch in subsequent frames.

Uses normalized cross-correlation; the search window slides with the last
known position so it works for modest motion between frames.
"""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


class TemplateTracker:
    """Simple single-object template tracker."""

    def __init__(self, template: NDArray[np.floating]) -> None:
        self._tpl = template.astype(np.float64)
        self._th, self._tw = template.shape[:2]

    def find(
        self,
        frame: NDArray[np.floating],
        *,
        search_radius: int | None = None,
    ) -> dict[str, float] | None:
        """Return best-match center ``{x, y, score}`` or None."""
        f = frame.astype(np.float64)
        h, w = f.shape[:2]
        if self._th >= h or self._tw >= w:
            return None
        gray_t = self._tpl.mean(axis=-1) if self._tpl.ndim == 3 else self._tpl
        gray_f = f.mean(axis=-1) if f.ndim == 3 else f
        radius = search_radius or max(self._th, self._tw)
        cy, cx = self._last_center if hasattr(self, "_last_center") else (h / 2, w / 2)
        y0 = max(0, int(cy - radius))
        y1 = min(h - self._th, int(cy + radius))
        x0 = max(0, int(cx - radius))
        x1 = min(w - self._tw, int(cx + radius))
        if y1 <= y0 or x1 <= x0:
            return None
        best_score, best_xy = -1.0, None
        for y in range(y0, y1, 2):
            for x in range(x0, x1, 2):
                patch = gray_f[y : y + self._th, x : x + self._tw]
                t = gray_t
                score = _ncc(patch, t)
                if score > best_score:
                    best_score, best_xy = score, (x + self._tw / 2, y + self._th / 2)
        if best_xy is None:
            return None
        self._last_center = best_xy
        return {"x": float(best_xy[0]), "y": float(best_xy[1]), "score": float(best_score)}

    def __call__(self, frame: NDArray[np.floating]) -> list[dict]:
        found = self.find(frame)
        return [found] if found else []


def _ncc(a: NDArray[np.floating], b: NDArray[np.floating]) -> float:
    a = a - a.mean()
    b = b - b.mean()
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom < 1e-9:
        return 0.0
    return float(np.sum(a * b) / denom)
