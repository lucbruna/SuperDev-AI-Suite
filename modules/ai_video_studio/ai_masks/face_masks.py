"""Face masks — build an elliptical mask from a face bbox."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def face_mask(shape: tuple[int, int], face: dict, *, soft: int = 4) -> NDArray[np.floating]:
    """Elliptical mask centered on ``face`` (x, y, w, h dict)."""
    h, w = shape
    cx, cy = face["x"], face["y"]
    fw, fh = face.get("w", w * 0.3), face.get("h", h * 0.4)
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.sqrt(((xx - cx) / max(1e-3, fw / 2)) ** 2 + ((yy - cy) / max(1e-3, fh / 2)) ** 2)
    m = np.clip(1 - r, 0.0, 1.0)
    if soft > 0:
        from .feather_engine import feather

        m = feather(m, soft)
    return m
