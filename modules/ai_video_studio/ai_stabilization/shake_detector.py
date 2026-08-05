"""Shake detection — rate the shakiness of a motion path."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def shake_score(path: NDArray[np.floating]) -> float:
    """Shake score 0..1 from a (N, 2) translation path.

    Uses high-frequency component magnitude relative to total motion.
    """
    if len(path) < 3:
        return 0.0
    deltas = np.diff(path, axis=0)
    speed = np.linalg.norm(deltas, axis=1)
    # High-frequency = frame-to-frame jitter (2nd difference)
    accel = np.abs(np.diff(speed, axis=0))
    total = speed.sum() + 1e-9
    high = accel.sum()
    return float(np.clip(high / (total + 1e-9) * 2.0, 0.0, 1.0))


def is_shaky(path: NDArray[np.floating], threshold: float = 0.25) -> bool:
    return shake_score(path) > threshold
