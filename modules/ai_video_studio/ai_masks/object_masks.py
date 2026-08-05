"""Object masks — rectangular/elliptical masks around object detections."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def box_mask(shape: tuple[int, int], box: dict, *, feather_px: int = 6) -> NDArray[np.floating]:
    """Soft-edged rectangle mask from a ``{x, y, w, h}`` detection box."""
    h, w = shape
    cx, cy = box["x"], box["y"]
    bw, bh = box.get("w", w * 0.4), box.get("h", h * 0.4)
    x0, x1 = int(cx - bw / 2), int(cx + bw / 2)
    y0, y1 = int(cy - bh / 2), int(cy + bh / 2)
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(w, x1), min(h, y1)
    m = np.zeros((h, w), dtype=np.float64)
    if x1 > x0 and y1 > y0:
        m[y0:y1, x0:x1] = 1.0
    if feather_px > 0:
        from .feather_engine import feather

        m = feather(m, max(1, feather_px // 3))
    return m
