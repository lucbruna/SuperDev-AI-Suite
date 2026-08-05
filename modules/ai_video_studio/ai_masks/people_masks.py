"""People masks — body-shaped mask from a person detection box."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def person_mask(shape: tuple[int, int], person: dict, *, soft: int = 5) -> NDArray[np.floating]:
    """Oval standing figure mask (narrower top, wider torso)."""
    h, w = shape
    cx, cy = person["x"], person["y"]
    bh = person.get("h", h * 0.5)
    bw = person.get("w", w * 0.18)
    yy, xx = np.mgrid[0:h, 0:w]
    # Head ellipse on top, body ellipse below
    head_r = np.sqrt(((xx - cx) / max(1e-3, bw)) ** 2 + ((yy - (cy - bh * 0.3)) / max(1e-3, bh * 0.35)) ** 2)
    body_r = np.sqrt(((xx - cx) / max(1e-3, bw * 1.2)) ** 2 + ((yy - cy) / max(1e-3, bh * 0.55)) ** 2)
    m = np.clip(1 - np.minimum(head_r, body_r), 0.0, 1.0)
    if soft > 0:
        from .feather_engine import feather

        m = feather(m, soft)
    return m
