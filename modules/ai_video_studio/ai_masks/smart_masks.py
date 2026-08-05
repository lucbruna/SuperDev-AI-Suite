"""Smart masks — automatic mask generation from simple heuristics."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def smart_mask(
    frame: NDArray[np.floating],
    *,
    mode: str = "center",
) -> NDArray[np.floating]:
    """Generate an automatic mask.

    Modes: ``center`` (elliptical center-weighted), ``sky`` (bright top),
    ``skin`` (skin-tone), ``vignette`` (soft radial falloff), ``silhouette``.
    """
    h, w = frame.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    if mode == "center":
        cx, cy = w / 2, h / 2
        r = np.sqrt(((xx - cx) / (w / 2)) ** 2 + ((yy - cy) / (h / 2)) ** 2)
        return np.clip(1 - r, 0.0, 1.0)
    if mode == "vignette":
        cx, cy = w / 2, h / 2
        r = np.sqrt(((xx - cx) / (w / 2)) ** 2 + ((yy - cy) / (h / 2)) ** 2)
        return np.clip(1 - (r - 0.55) / 0.45, 0.0, 1.0)
    if mode == "sky":
        luma = frame.mean(axis=-1)
        bright_top = luma > np.percentile(luma[: max(1, h // 3)], 50)
        return bright_top.astype(np.float64)
    if mode == "skin":
        f = frame.astype(np.float64)
        r, g, b = f[..., 0], f[..., 1], f[..., 2]
        with np.errstate(divide="ignore", invalid="ignore"):
            nr = r / np.maximum(r + g + b, 1e-6)
        return ((nr > 0.35) & (r > 0.3)).astype(np.float64)
    if mode == "silhouette":
        luma = frame.mean(axis=-1)
        return (luma < luma.mean()).astype(np.float64)
    raise ValueError(f"unknown smart mask mode {mode!r}")
