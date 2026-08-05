"""Birds Generator — FM chirps sweeping upward."""
from __future__ import annotations

import numpy as np

from modules.ai_video_studio.media import dsp


def generate(duration: float, *, sample_rate: int = dsp.SAMPLE_RATE, seed: int = 0,
             count: int | None = None, **_: object) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = int(duration * sample_rate)
    out = np.zeros(n, dtype=np.float64)
    count = count if count is not None else max(2, int(duration))
    for _ in range(count):
        start = int(rng.integers(0, n - int(0.5 * sample_rate)))
        length = int(rng.integers(1200, 3200))
        tt = np.arange(length) / sample_rate
        f0 = rng.uniform(1800, 3800)
        f1 = f0 * rng.uniform(1.4, 2.2)
        freq = f0 + (f1 - f0) * (tt / max(tt[-1], 1e-6))
        phase = 2 * np.pi * np.cumsum(freq) / sample_rate
        chirp = np.sin(phase)
        chirp += 0.4 * np.sin(2 * phase)  # rich birdsong harmonics
        env = dsp.adsr(length, attack=0.01, decay=0.1, sustain=0.5, release=0.1,
                       sample_rate=sample_rate)
        out[start:start + length] += chirp * env * rng.uniform(0.2, 0.5)
    return dsp.normalize_peak(out, 0.8).astype(np.float32)
