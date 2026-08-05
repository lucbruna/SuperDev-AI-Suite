"""Alpha composition helpers."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def straight_alpha(
    bg: NDArray[np.floating],
    fg: NDArray[np.floating],
    alpha: NDArray[np.floating] | None = None,
) -> NDArray[np.floating]:
    """Standard 'over' operator with straight alpha."""
    a = np.ones_like(bg[..., :1]) if alpha is None else alpha[..., :1]
    a = np.clip(a, 0.0, 1.0)
    out = bg * (1 - a) + fg * a
    return np.clip(out, 0.0, 1.0)


def premultiplied_alpha(
    bg: NDArray[np.floating],
    fg_premul: NDArray[np.floating],
    alpha: NDArray[np.floating],
) -> NDArray[np.floating]:
    """Over operator for premultiplied foreground."""
    a = np.clip(alpha[..., :1], 0.0, 1.0)
    out = bg * (1 - a) + fg_premul
    return np.clip(out, 0.0, 1.0)


def feather_mask(mask: NDArray[np.floating], radius: int = 1) -> NDArray[np.floating]:
    """Soft-feather a binary mask via iterative box blur."""
    m = mask[..., :1] if mask.ndim == 3 else mask[..., None]
    if radius <= 0:
        return m
    for _ in range(radius):
        m = _box(m)
    return np.clip(m, 0.0, 1.0)


def _box(m: NDArray[np.floating]) -> NDArray[np.floating]:
    kernel = np.array([1, 2, 1], dtype=np.float64)
    from scipy.ndimage import convolve  # type: ignore[import-not-found]

    return convolve(m[..., 0], kernel[:, None] * kernel[None, :], mode="nearest")[..., None] / 16.0
