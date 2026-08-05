"""Vehicle masks — box mask with a darker (wheel) emphasis strip."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def vehicle_mask(shape: tuple[int, int], vehicle: dict) -> NDArray[np.floating]:
    """Soft rectangle mask with slightly stronger lower third (wheels)."""
    h, w = shape
    cx, cy = vehicle["x"], vehicle["y"]
    bw = vehicle.get("w", w * 0.35)
    bh = vehicle.get("h", h * 0.25)
    x0, x1 = int(cx - bw / 2), int(cx + bw / 2)
    y0, y1 = int(cy - bh / 2), int(cy + bh / 2)
    m = np.zeros((h, w), dtype=np.float64)
    x0, y0, x1, y1 = max(0, x0), max(0, y0), min(w, x1), min(h, y1)
    if x1 > x0 and y1 > y0:
        m[y0:y1, x0:x1] = 1.0
        m[y0 + int((y1 - y0) * 0.6) : y1, x0:x1] = 1.0  # wheels emphasis (already 1)
    from .feather_engine import feather

    return feather(m, 2)
