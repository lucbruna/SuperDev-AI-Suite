"""Scratch removal — remove vertical film scratches via streak inpainting."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def remove_scratches(
    frame: NDArray[np.floating],
    *,
    threshold: float = 0.5,
    width_max: int = 3,
) -> NDArray[np.floating]:
    """Detect vertical streaks and replace them with a horizontal median."""
    f = frame.astype(np.float64)
    luma = f.mean(axis=-1)
    # Vertical streak = column whose median deviates from neighbors
    col_med = np.median(luma, axis=0)
    col_med_smooth = np.convolve(col_med, np.ones(5) / 5, mode="same")
    dev = np.abs(col_med - col_med_smooth) / (col_med_smooth + 1e-9)
    scratch_cols = np.where(dev > threshold)[0]
    if len(scratch_cols) == 0:
        return f
    out = f.copy()
    for col in scratch_cols:
        if col < width_max or col >= f.shape[1] - width_max:
            continue
        left = col - width_max
        right = col + width_max + 1
        # Replace with the average of clean neighbor columns
        replacement = (f[:, col - width_max - 1] + f[:, col + width_max + 1]) / 2
        out[:, left:right] = replacement[:, None, :]
    return out
