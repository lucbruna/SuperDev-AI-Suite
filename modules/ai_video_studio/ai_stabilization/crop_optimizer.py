"""Crop optimizer — minimal border crop that hides stabilization artifacts."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def safe_crop(path: NDArray[np.floating], smoothed: NDArray[np.floating], *, frame_w: int, frame_h: int) -> int:
    """Return the smallest border crop (px) covering correction motion."""
    if len(path) == 0:
        return 0
    corr = np.abs(path - smoothed)
    if corr.size == 0:
        return 0
    max_disp = float(corr.max())
    # Add a small margin so edges never peek
    margin = max(2, int(round(max_disp * 1.2)) + 1)
    return min(margin, min(frame_w, frame_h) // 2 - 1)


def crop_frame(frame: NDArray[np.floating], crop: int) -> NDArray[np.floating]:
    """Crop evenly from all borders."""
    if crop <= 0:
        return frame
    h, w = frame.shape[:2]
    y0, y1 = crop, h - crop
    x0, x1 = crop, w - crop
    if y1 <= y0 or x1 <= x0:
        return frame
    return frame[y0:y1, x0:x1]
