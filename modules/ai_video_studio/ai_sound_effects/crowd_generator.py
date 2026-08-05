"""Crowd Generator — babble bed with applause-like swells."""
from __future__ import annotations

import numpy as np

from modules.ai_video_studio.media import dsp


def generate(duration: float, *, sample_rate: int = dsp.SAMPLE_RATE, seed: int = 0,
             intensity: float = 0.6, **_: object) -> np.ndarray:
    n = int(duration * sample_rate)
    t = np.arange(n) / sample_rate
    babble = dsp.noise_white(duration, sample_rate=sample_rate, seed=seed)[:n]
    babble = dsp.biquad_peak(babble, 700.0, 0.7, 10.0, sample_rate=sample_rate)
    babble = dsp.biquad_peak(babble, 1800.0, 0.8, 6.0, sample_rate=sample_rate)
    # Slow excitement swells.
    swell = 0.5 + 0.5 * np.sin(2 * np.pi * 0.17 * t + seed) ** 2
    # Sparse hand-clap bursts.
    rng = np.random.default_rng(seed + 1)
    claps = np.zeros(n, dtype=np.float64)
    for _ in range(int(duration * 0.6)):
        start = int(rng.integers(0, n - 4000))
        length = 1200
        burst = dsp.noise_white(length / sample_rate, sample_rate=sample_rate,
                                seed=int(rng.integers(0, 9999)))[:length]
        burst = dsp.biquad_peak(burst, 2500.0, 1.2, 4.0, sample_rate=sample_rate)
        claps[start:start + length] += burst * 0.2
    out = babble * swell * intensity + claps
    return dsp.normalize_peak(out, 0.9).astype(np.float32)
