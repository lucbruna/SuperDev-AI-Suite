"""Video denoising — fast box denoise blended by local variance."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def denoise(frame: NDArray[np.floating], *, strength: float = 0.3, kernel: int = 3) -> NDArray[np.floating]:
    """Denoise: blend the frame with its box-filtered version.

    The blend factor is higher in flat (low variance) regions, preserving
    edges and textures.
    """
    f = frame.astype(np.float64)
    blurred = _box(f, kernel)
    variance = np.mean((f - blurred) ** 2, axis=-1, keepdims=True)
    flatness = np.exp(-variance / (0.02 + 1e-9))
    alpha = np.clip(flatness * strength, 0.0, 1.0)
    return f * (1 - alpha) + blurred * alpha


def _box(a: NDArray[np.floating], k: int) -> NDArray[np.floating]:
    from scipy.ndimage import uniform_filter  # type: ignore[import-not-found]

    if a.ndim == 3:
        return uniform_filter(a, size=(k, k, 1), mode="nearest")
    return uniform_filter(a, size=k, mode="nearest")
