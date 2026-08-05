"""Flanger — 0.5-5 ms modulated delay with feedback (jet/sweep sound)."""
from __future__ import annotations

import numpy as np

from modules.ai_video_studio.media import dsp


def flanger(x: np.ndarray, *, depth: float = 0.002, rate: float = 0.25,
            feedback: float = 0.3, mix: float = 0.5,
            sample_rate: int = dsp.SAMPLE_RATE) -> np.ndarray:
    if mix <= 0:
        return x.copy()
    n = len(x)
    base = int(0.001 * sample_rate)
    depth_samples = max(1, int(depth * sample_rate))
    out = np.zeros(n, dtype=np.float64)
    state = 0.0
    for i in range(n):
        mod = base + depth_samples * (0.5 + 0.5 * np.sin(2 * np.pi * rate * i / sample_rate))
        idx = int(i - mod)
        delayed = out[idx] if 0 <= idx < n else 0.0
        state = x[i] + feedback * delayed
        out[i] = x[i] + mix * state
    return dsp.normalize_peak(out, dsp.peak(x) + 1e-9).astype(np.float32)
