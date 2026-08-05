"""Face tracking — lightweight skin-tone detector + template follow.

A real deployment plugs a face detection model (e.g. MediaPipe/FaceNet)
into :class:`TrackingEngine`; this heuristic keeps pipelines functional
offline.
"""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from .object_tracking import TemplateTracker


class FaceTracker:
    """Skin-color blob face detector with deterministic output."""

    def __init__(self, min_face_ratio: float = 0.02) -> None:
        self._min_ratio = min_face_ratio
        self._follow: TemplateTracker | None = None

    def __call__(self, frame: NDArray[np.floating]) -> list[dict]:
        f = frame.astype(np.float64)
        h, w = f.shape[:2]
        r, g, b = f[..., 0], f[..., 1], f[..., 2]
        # Classic skin-color heuristic in normalized RGB
        with np.errstate(divide="ignore", invalid="ignore"):
            denom = np.maximum(r + g + b, 1e-6)
            nr, ng = r / denom, g / denom
        mask = (nr > 0.2) & (ng > 0.15) & (np.abs(nr - ng) < 0.12) & (r > 0.25)
        ys, xs = np.where(mask)
        if len(xs) < h * w * self._min_ratio:
            return []
        cx, cy = float(xs.mean()), float(ys.mean())
        bw, bh = float(xs.max() - xs.min()), float(ys.max() - ys.min())
        return [{"x": cx, "y": cy, "w": bw, "h": bh, "score": 1.0, "kind": "face"}]
