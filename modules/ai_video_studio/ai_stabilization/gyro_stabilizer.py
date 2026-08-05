"""Gyro stabilizer — translate gyroscope samples into camera displacement."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def integrate_gyro(
    gyro: NDArray[np.floating],
    *,
    dt: float = 1 / 240.0,
    sensitivity: float = 1.0,
) -> NDArray[np.floating]:
    """Double-integrate angular velocity into (x, y) displacement.

    ``gyro`` shape (N, 3) with angular rates in rad/s (roll, pitch, yaw).
    """
    gyro = np.asarray(gyro, dtype=np.float64)
    angle = np.cumsum(gyro * dt, axis=0)
    # Map pitch/yaw to screen-space translation
    disp = angle[:, [1, 0]] * sensitivity
    # Remove linear drift for stabilization baseline
    disp = disp - np.linspace(disp[0], disp[-1], len(disp))
    return disp


def smooth_gyro(disp: NDArray[np.floating], *, alpha: float = 0.5) -> NDArray[np.floating]:
    """Smooth a displacement curve for a stabilized path."""
    from .camera_smoothing import smooth_trajectory

    return smooth_trajectory(disp, alpha=alpha)
