"""Camera smoothing — trajectory filters."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def smooth_trajectory(path: NDArray[np.floating], *, alpha: float = 0.6) -> NDArray[np.floating]:
    """Exponential moving average of a (N, 2) path."""
    if len(path) == 0:
        return path
    out = np.zeros_like(path)
    out[0] = path[0]
    for i in range(1, len(path)):
        out[i] = alpha * out[i - 1] + (1 - alpha) * path[i]
    return out


def low_pass(path: NDArray[np.floating], *, window: int = 5) -> NDArray[np.floating]:
    """Moving-average low-pass filter over the path."""
    if len(path) <= window:
        return path.copy()
    kernel = np.ones(window) / window
    out = np.zeros_like(path)
    for col in range(path.shape[1]):
        padded = np.pad(path[:, col], (window // 2, window // 2), mode="edge")
        out[:, col] = np.convolve(padded, kernel, mode="valid")
    return out
