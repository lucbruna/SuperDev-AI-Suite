"""Color restoration — white balance + contrast stretch for faded footage."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def restore_color(
    frame: NDArray[np.floating],
    *,
    balance: float = 1.0,
    stretch: float = 0.02,
) -> NDArray[np.floating]:
    """Auto white-balance + percentile contrast stretch."""
    f = frame.astype(np.float64)
    # Gray-world white balance
    means = f.mean(axis=(0, 1))
    target = means.mean()
    gains = np.where(means > 1e-9, (target / means) ** balance, 1.0)
    out = f * gains[None, None, :]
    # Percentile stretch per channel
    if stretch > 0:
        lo = np.percentile(out, stretch * 100, axis=(0, 1))
        hi = np.percentile(out, 100 - stretch * 100, axis=(0, 1))
        out = (out - lo) / (hi - lo + 1e-9)
    return np.clip(out, 0.0, 1.0)
