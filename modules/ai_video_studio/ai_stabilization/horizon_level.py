"""Horizon leveling — detect the dominant line and rotate it level."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def estimate_angle(frame: NDArray[np.floating]) -> float:
    """Estimate the horizon tilt angle (radians) via edge histogram.

    Uses the Hough-lite approach: strong horizontal-ish edges vote on angle.
    """
    luma = frame.mean(axis=-1).astype(np.float64)
    gy = np.gradient(luma, axis=0)
    gx = np.gradient(luma, axis=1)
    mag = np.hypot(gx, gy)
    strong = mag > np.percentile(mag, 92)
    if strong.sum() < 10:
        return 0.0
    angles = np.arctan2(gy[strong], gx[strong])
    # Weight horizontal-ish edges (|angle| near 0 or pi)
    weight = np.cos(angles * 2) ** 2
    if weight.sum() < 1e-9:
        return 0.0
    mean_angle = float(np.sum(angles * weight) / weight.sum())
    # Normalize to the nearest horizontal
    return _to_horizontal(mean_angle)


def _to_horizontal(a: float) -> float:
    while a > np.pi / 2:
        a -= np.pi
    while a < -np.pi / 2:
        a += np.pi
    return a


def level_horizon(frame: NDArray[np.floating], *, max_angle: float = 0.3) -> NDArray[np.floating]:
    """Rotate the frame to level the horizon (crops borders)."""
    from scipy.ndimage import rotate  # type: ignore[import-not-found]

    angle = estimate_angle(frame)
    if abs(angle) < 0.005 or abs(angle) > max_angle:
        return frame
    return rotate(frame, np.degrees(angle), reshape=False, order=1, mode="nearest")
