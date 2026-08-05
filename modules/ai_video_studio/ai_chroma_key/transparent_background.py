"""Transparent background — convert keyed frame to RGBA."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def to_rgba(
    frame: NDArray[np.floating],
    matte: NDArray[np.floating],
) -> NDArray[np.floating]:
    """Return an RGBA frame (H, W, 4) with the matte as alpha."""
    m = matte[..., None] if matte.ndim == 2 else matte[..., :1]
    rgba = np.concatenate([frame[..., :3], np.clip(m, 0.0, 1.0)], axis=-1)
    return rgba
