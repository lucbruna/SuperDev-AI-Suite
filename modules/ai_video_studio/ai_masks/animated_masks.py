"""Animated masks — time-interpolated mask sequences."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def interpolate_mask(keyframes: list[tuple[float, NDArray[np.floating]]], t: float) -> NDArray[np.floating]:
    """Linearly interpolate masks between keyframes ``(time, mask)`` pairs."""
    if not keyframes:
        raise ValueError("no keyframes")
    times = [k[0] for k in keyframes]
    if t <= times[0]:
        return keyframes[0][1].astype(np.float64)
    if t >= times[-1]:
        return keyframes[-1][1].astype(np.float64)
    for (t0, m0), (t1, m1) in zip(keyframes, keyframes[1:], strict=False):
        if t0 <= t <= t1:
            alpha = (t - t0) / max(1e-9, t1 - t0)
            return np.clip(m0 * (1 - alpha) + m1 * alpha, 0.0, 1.0)
    return keyframes[-1][1].astype(np.float64)


def translate_mask(mask: NDArray[np.floating], dx: int, dy: int, shape: tuple[int, int]) -> NDArray[np.floating]:
    """Shift a mask within ``shape`` (clipped)."""
    h, w = shape
    m = mask[..., 0] if mask.ndim == 3 else mask
    out = np.zeros((h, w), dtype=np.float64)
    src_y0, src_x0 = max(0, -dy), max(0, -dx)
    dst_y0, dst_x0 = max(0, dy), max(0, dx)
    src_y1 = min(h, m.shape[0] - dy) if dy >= 0 else min(h, m.shape[0])
    src_x1 = min(w, m.shape[1] - dx) if dx >= 0 else min(w, m.shape[1])
    src_y1 = min(src_y1, m.shape[0])
    src_x1 = min(src_x1, m.shape[1])
    dst_y1 = min(h, src_y1 + dy)
    dst_x1 = min(w, src_x1 + dx)
    out[dst_y0:dst_y1, dst_x0:dst_x1] = m[src_y0:src_y1, src_x0:src_x1]
    return out
