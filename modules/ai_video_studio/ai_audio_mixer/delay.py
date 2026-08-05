"""Delay — feedback delay line with mix control."""
from __future__ import annotations

import numpy as np

from modules.ai_video_studio.media import dsp


def delay(x: np.ndarray, *, seconds: float = 0.35, feedback: float = 0.35,
          mix: float = 0.3, sample_rate: int = dsp.SAMPLE_RATE) -> np.ndarray:
    """Classic feedback delay."""
    if mix <= 0:
        return x.copy()
    wet = dsp.comb(x, seconds, feedback, sample_rate=sample_rate)
    return ((1 - mix) * x + mix * wet).astype(np.float32)


def ping_pong(x: np.ndarray, *, seconds: float = 0.3, feedback: float = 0.4,
              sample_rate: int = dsp.SAMPLE_RATE) -> np.ndarray:
    """Stereo ping-pong delay (input may be mono or stereo)."""
    mono = x.reshape(-1) if x.ndim == 1 else np.mean(x, axis=-1)
    left = np.zeros_like(mono, dtype=np.float64)
    right = np.zeros_like(mono, dtype=np.float64)
    delay_samples = int(seconds * sample_rate)
    left[: len(mono)] = mono
    for i in range(len(mono)):
        if i >= delay_samples:
            right[i] = 0.6 * left[i - delay_samples]
        if i >= 2 * delay_samples:
            left[i] += 0.5 * right[i - delay_samples] * feedback
    out = np.stack([left, right], axis=-1)
    return dsp.normalize_peak(out, 0.95).astype(np.float32)
