"""Stereo Enhancer — widens the image via mid/side processing."""
from __future__ import annotations

import numpy as np

from modules.ai_video_studio.media import dsp


def to_mid_side(stereo: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    left, right = stereo[:, 0], stereo[:, 1]
    mid = (left + right) / 2.0
    side = (left - right) / 2.0
    return mid, side


def from_mid_side(mid: np.ndarray, side: np.ndarray) -> np.ndarray:
    left = mid + side
    right = mid - side
    return np.stack([left, right], axis=-1)


def widen(stereo: np.ndarray, *, amount: float = 0.3,
          sample_rate: int = dsp.SAMPLE_RATE) -> np.ndarray:
    """Widen (positive) or narrow (negative) the stereo image."""
    if stereo.ndim != 2 or stereo.shape[1] != 2:
        return to_stereo_mix(stereo)
    mid, side = to_mid_side(stereo)
    side = side * (1.0 + amount)
    out = from_mid_side(mid, side)
    return dsp.normalize_peak(out, 0.98).astype(np.float32)


def to_stereo_mix(x: np.ndarray) -> np.ndarray:
    mono = np.asarray(x).reshape(-1)
    return np.stack([mono, mono], axis=-1).astype(np.float32)
