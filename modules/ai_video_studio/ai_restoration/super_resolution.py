"""Super resolution — bicubic upscale with a detail-enhancement pass."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def upscale(frame: NDArray[np.floating], factor: float = 2.0, *, detail: float = 0.3) -> NDArray[np.floating]:
    """Upscale by ``factor`` (>=1) using bicubic interpolation."""
    if factor <= 1.0:
        return frame
    from scipy.ndimage import zoom  # type: ignore[import-not-found]

    f = frame.astype(np.float64)
    factors = (factor, factor, 1.0)
    out = zoom(f, factors, order=3, mode="nearest")
    if detail > 0:
        from .deblur_video import deblur

        out = deblur(out, strength=detail)
    return np.clip(out, 0.0, 1.0)


def fast_upscale(frame: NDArray[np.floating], factor: float = 2.0) -> NDArray[np.floating]:
    """Nearest-neighbor upscale (fast preview path)."""
    if factor <= 1.0:
        return frame
    from scipy.ndimage import zoom  # type: ignore[import-not-found]

    return np.clip(zoom(frame, (factor, factor, 1.0), order=0, mode="nearest"), 0.0, 1.0)
