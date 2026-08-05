"""Feather engine — soften mask boundaries."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def feather(mask: NDArray[np.floating], radius: int = 2) -> NDArray[np.floating]:
    """Box-blur the mask edge ``radius`` times (fast, deterministic)."""
    m = mask[..., 0] if mask.ndim == 3 else mask
    out = m.astype(np.float64)
    k = max(1, radius)
    for _ in range(k):
        out = _box_blur(out)
    return np.clip(out, 0.0, 1.0)


def _box_blur(a: NDArray[np.floating]) -> NDArray[np.floating]:
    h, w = a.shape
    padded = np.pad(a, 1, mode="edge")
    # horizontal
    tmp = (padded[:, :-2] + padded[:, 1:-1] + padded[:, 2:]) / 3.0
    padded = np.pad(tmp, ((1, 1), (0, 0)), mode="edge")
    out = (padded[:-2] + padded[1:-1] + padded[2:]) / 3.0
    return out[:h, :w]
