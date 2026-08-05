"""Optical flow wrapper — uses the motion tracker for dense displacement."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def dense_flow(a: NDArray[np.floating], b: NDArray[np.floating]) -> np.ndarray:
    """Return a (H, W, 2) flow field (downsampled then upscaled)."""
    from ..ai_tracking.motion_tracking import MotionTracker

    tracker = MotionTracker(grid=16)
    result = tracker.compute_flow(a, b)
    h, w = a.shape[:2]
    flow = np.zeros((h, w, 2), dtype=np.float64)
    for pt, vec in zip(result["points"], result["vectors"], strict=False):
        y, x = int(pt["y"]), int(pt["x"])
        if 0 <= x < w and 0 <= y < h:
            flow[y, x] = (vec["dx"], vec["dy"])
    # Fill empty cells by nearest-neighbor propagation (bilateral-ish)
    from scipy.ndimage import distance_transform_edt  # type: ignore[import-not-found]

    valid = (flow[..., 0] != 0) | (flow[..., 1] != 0)
    if valid.any():
        filled = np.zeros_like(flow)
        filled[valid] = flow[valid]
        # Propagate using EDT-based nearest valid sample per channel

        np.indices((h, w))
        for c in range(2):
            idx = np.argwhere(valid)
            if len(idx) == 0:
                continue
            dist, nearest = distance_transform_edt(~valid, return_indices=True)
            filled[..., c] = flow[..., c][nearest[0], nearest[1]]
        return filled
    return flow
