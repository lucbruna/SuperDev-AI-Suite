"""Matte generation — luminance, chroma and color-range keying helpers."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def luminance_matte(frame: NDArray[np.floating], *, lo: float = 0.1, hi: float = 0.9) -> NDArray[np.floating]:
    """Soft luminance key: 0 below ``lo``, 1 above ``hi``, linear ramp between."""
    luma = frame[..., :3].mean(axis=-1)
    return np.clip((luma - lo) / max(1e-6, hi - lo), 0.0, 1.0)


def chroma_matte(
    frame: NDArray[np.floating],
    *,
    key_color: tuple[float, float, float],
    tolerance: float = 0.35,
    softness: float = 0.1,
) -> NDArray[np.floating]:
    """Distance-based chroma key (euclidean in RGB)."""
    k = np.asarray(key_color, dtype=np.float64)
    dist = np.linalg.norm(frame[..., :3] - k, axis=-1)
    inner = max(1e-6, tolerance)
    outer = inner + max(1e-6, softness)
    return np.clip((dist - inner) / (outer - inner), 0.0, 1.0)


def color_range_matte(
    frame: NDArray[np.floating],
    *,
    low: tuple[float, float, float],
    high: tuple[float, float, float],
) -> NDArray[np.floating]:
    """Binary box matte for pixels inside ``low``..``high``."""
    f = frame[..., :3]
    inside = np.all((f >= np.asarray(low)) & (f <= np.asarray(high)), axis=-1)
    return inside.astype(np.float64)


def feather_mask(
    mask: NDArray[np.floating],
    *,
    radius: int = 1,
) -> NDArray[np.floating]:
    """Smooth a mask (HxW or HxWx1) with a box filter, keeping it in [0, 1].

    A small ``radius`` softens the edges of keyed mattes without a full
    Gaussian — fast and dependency-light.
    """
    m = mask.astype(np.float64)
    if m.ndim == 3 and m.shape[2] == 1:
        m = m[..., 0]
    radius = max(0, int(radius))
    if radius == 0:
        return np.clip(mask, 0.0, 1.0)
    kernel = radius * 2 + 1
    try:
        from scipy.ndimage import uniform_filter

        out = uniform_filter(m, size=kernel, mode="nearest")
    except Exception:  # pragma: no cover — manual fallback
        from modules.ai_video_studio.editor_common import box_filter

        out = box_filter(m, kernel)
    return np.clip(out, 0.0, 1.0)


def despill(
    frame: NDArray[np.floating],
    matte: NDArray[np.floating],
    *,
    key_color: tuple[float, float, float],
    amount: float = 0.5,
) -> NDArray[np.floating]:
    """Reduce color spill around matte edges (screen color bleed)."""
    k = np.asarray(key_color, dtype=np.float64)
    spill = np.clip(frame[..., :3] - k, 0.0, None) * matte[..., None] * amount
    return np.clip(frame[..., :3] - spill * 0.5, 0.0, 1.0)
