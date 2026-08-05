"""Chorus — LFO-modulated delay (~30 ms) for thickening."""
from __future__ import annotations

import numpy as np

from modules.ai_video_studio.media import dsp


def chorus(x: np.ndarray, *, depth: float = 0.01, rate: float = 0.5,
           mix: float = 0.5, sample_rate: int = dsp.SAMPLE_RATE) -> np.ndarray:
    if mix <= 0:
        return x.copy()
    n = len(x)
    base = int(0.03 * sample_rate)
    depth_samples = int(depth * sample_rate)
    out = np.zeros_like(x, dtype=np.float64)
    for i in range(n):
        mod = base + depth_samples * (0.5 + 0.5 * np.sin(2 * np.pi * rate * i / sample_rate))
        idx = int(i - mod)
        delayed = x[idx] if 0 <= idx < n else 0.0
        out[i] = x[i] + mix * delayed
    return dsp.normalize_peak(out, dsp.peak(x) + 1e-9).astype(np.float32)
