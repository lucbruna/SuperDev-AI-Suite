"""Compressor — dynamics processing with smoothed gain reduction."""
from __future__ import annotations

import numpy as np

from modules.ai_video_studio.media import dsp


def compress(x: np.ndarray, *, threshold_db: float = -18.0, ratio: float = 3.0,
             attack: float = 0.005, release: float = 0.12, makeup_db: float = 0.0,
             sample_rate: int = dsp.SAMPLE_RATE) -> np.ndarray:
    """Compress ``x``; returns the processed signal (same length)."""
    if len(x) == 0:
        return x
    threshold = 10 ** (threshold_db / 20.0)
    env = np.abs(x.astype(np.float64))
    at = np.exp(-1.0 / (attack * sample_rate))
    rt = np.exp(-1.0 / (release * sample_rate))
    n = len(x)
    gain = np.ones(n, dtype=np.float64)
    smoothed = 0.0
    for i in range(n):
        level = env[i]
        if level > smoothed:  # noqa: SIM108 — clearer as a branch
            smoothed = at * smoothed + (1 - at) * level
        else:
            smoothed = rt * smoothed + (1 - rt) * level
        if smoothed > threshold:
            over = smoothed / threshold
            # compression ratio applied above threshold
            target = threshold * over ** (1.0 / ratio)
            gain[i] = target / smoothed
        else:
            gain[i] = 1.0
    makeup = 10 ** (makeup_db / 20.0)
    return (x * gain * makeup).astype(np.float32)
