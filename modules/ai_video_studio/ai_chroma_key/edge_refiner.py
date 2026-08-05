"""Edge refinement for keyed mattes."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from ..ai_compositor.matte_generator import feather_mask


def refine_edges(
    matte: NDArray[np.floating],
    *,
    erode: int = 0,
    dilate: int = 0,
    smooth: int = 1,
) -> NDArray[np.floating]:
    """Erode/dilate the matte (int pixels) and optionally smooth it."""
    m = matte.astype(np.float64)
    if erode > 0:
        m = _shrink(m, erode)
    if dilate > 0:
        m = _expand(m, dilate)
    if smooth > 0:
        m = feather_mask(m[..., None], radius=smooth)[..., 0]
    return np.clip(m, 0.0, 1.0)


def _shrink(m: NDArray[np.float64], n: int) -> NDArray[np.float64]:
    out = m.copy()
    for _ in range(n):
        out = np.minimum(out, np.roll(out, 1, axis=0))
        out = np.minimum(out, np.roll(out, -1, axis=0))
        out = np.minimum(out, np.roll(out, 1, axis=1))
        out = np.minimum(out, np.roll(out, -1, axis=1))
    return out


def _expand(m: NDArray[np.float64], n: int) -> NDArray[np.float64]:
    out = m.copy()
    for _ in range(n):
        out = np.maximum(out, np.roll(out, 1, axis=0))
        out = np.maximum(out, np.roll(out, -1, axis=0))
        out = np.maximum(out, np.roll(out, 1, axis=1))
        out = np.maximum(out, np.roll(out, -1, axis=1))
    return out
