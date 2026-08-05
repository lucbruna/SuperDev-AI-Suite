"""Video deblurring — high-pass sharpening approximation of deconvolution."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def deblur(frame: NDArray[np.floating], *, strength: float = 0.4, kernel: int = 3) -> NDArray[np.floating]:
    """Unsharp-mask deblur: add back the high-frequency detail."""
    f = frame.astype(np.float64)
    blurred = _box(f, kernel)
    detail = f - blurred
    return np.clip(f + detail * strength, 0.0, 1.0)


def _box(a: NDArray[np.floating], k: int) -> NDArray[np.floating]:
    from scipy.ndimage import uniform_filter  # type: ignore[import-not-found]

    return uniform_filter(a, size=(k, k, 1) if a.ndim == 3 else k, mode="nearest")
