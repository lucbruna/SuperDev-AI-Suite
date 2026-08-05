"""Dust removal — median-filter small bright/dark specks (dust)."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def remove_dust(
    frame: NDArray[np.floating],
    *,
    kernel: int = 3,
    sensitivity: float = 0.25,
) -> NDArray[np.floating]:
    """Replace isolated outlier pixels with the local median."""
    from scipy.ndimage import median_filter  # type: ignore[import-not-found]

    f = frame.astype(np.float64)
    med = median_filter(f, size=(kernel, kernel, 1) if f.ndim == 3 else kernel, mode="nearest")
    dev = np.abs(f - med)
    outlier = dev > sensitivity
    # Keep only isolated specks (erode the mask to avoid edges)
    outlier = _erode(outlier)
    return np.where(outlier, med, f)


def _erode(mask: NDArray[np.bool_]) -> NDArray[np.bool_]:
    out = mask.copy()
    for axis in (0, 1):
        out &= np.roll(mask, 1, axis=axis)
        out &= np.roll(mask, -1, axis=axis)
    return out
