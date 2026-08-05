"""Object extraction — foreground with alpha, cropped to subject bbox."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def extract_object(
    frame: NDArray[np.floating],
    matte: NDArray[np.floating],
    *,
    crop: bool = True,
    pad: int = 4,
) -> NDArray[np.floating]:
    """Return RGBA foreground. With ``crop``, tight bbox around the subject."""
    m = matte[..., None] if matte.ndim == 2 else matte[..., :1]
    alpha = np.clip(m, 0.0, 1.0)
    rgba = np.concatenate([frame[..., :3] * alpha, alpha], axis=-1)
    if not crop:
        return rgba
    ys, xs = np.where(alpha[..., 0] > 0.05)
    if len(xs) == 0:
        return rgba
    y0, y1 = max(0, ys.min() - pad), min(alpha.shape[0], ys.max() + pad + 1)
    x0, x1 = max(0, xs.min() - pad), min(alpha.shape[1], xs.max() + pad + 1)
    return rgba[y0:y1, x0:x1]
