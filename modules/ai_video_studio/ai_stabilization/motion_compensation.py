"""Motion compensation — warp a frame according to a flow/displacement map."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def warp_with_flow(
    frame: NDArray[np.floating],
    flow: NDArray[np.floating],
) -> NDArray[np.floating]:
    """Remap ``frame`` using backward flow field (H, W, 2)."""
    from scipy.ndimage import map_coordinates  # type: ignore[import-not-found]

    h, w = frame.shape[:2]
    if flow.shape[:2] != (h, w):
        raise ValueError("flow must match frame shape")
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float64)
    # backward warp: sample source at (y - dy, x - dx)
    sy = np.clip(yy - flow[..., 1], 0, h - 1)
    sx = np.clip(xx - flow[..., 0], 0, w - 1)
    out = np.zeros_like(frame)
    for c in range(frame.shape[2]):
        out[..., c] = map_coordinates(frame[..., c], [sy, sx], order=1, mode="nearest")
    return np.clip(out, 0.0, 1.0)
