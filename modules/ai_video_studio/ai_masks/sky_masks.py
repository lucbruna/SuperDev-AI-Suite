"""Sky masks — heuristic sky detection (bright, bluish, upper frame)."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def sky_mask(frame: NDArray[np.floating], *, threshold: float = 0.15) -> NDArray[np.floating]:
    """Sky mask: bright bluish pixels weighted toward the top half."""
    f = frame.astype(np.float64)
    r, _g, b = f[..., 0], f[..., 1], f[..., 2]
    luma = f.mean(axis=-1)
    blue_dominant = (b - r) / np.maximum(luma + 1e-6, 1e-6)
    bright = luma > 0.35
    bluish = blue_dominant > threshold
    m = (bright & bluish).astype(np.float64)
    # Height weighting: sky lives at top
    h = frame.shape[0]
    yy = np.arange(h)[:, None] / max(1, h)
    m = m * np.clip(1.6 - 1.6 * yy, 0.3, 1.0)
    return np.clip(m, 0.0, 1.0)
