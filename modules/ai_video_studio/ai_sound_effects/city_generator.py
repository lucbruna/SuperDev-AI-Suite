"""City Generator — traffic bed with periodic car horns."""
from __future__ import annotations

import numpy as np

from modules.ai_video_studio.media import dsp


def generate(duration: float, *, sample_rate: int = dsp.SAMPLE_RATE, seed: int = 0,
             intensity: float = 0.6, **_: object) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = int(duration * sample_rate)
    traffic = dsp.noise_brown(duration, sample_rate=sample_rate, seed=seed)[:n]
    traffic = dsp.one_pole_lp(traffic, 700.0, sample_rate=sample_rate)
    # Passing vehicles: periodic band-passed swells.
    t = np.arange(n) / sample_rate
    swell = 0.5 + 0.5 * np.sin(2 * np.pi * 0.22 * t + seed)
    out = traffic * swell * intensity

    horn_count = int(duration / 6)
    for _ in range(horn_count):
        start = int(rng.integers(int(0.5 * sample_rate), n - int(sample_rate)))
        length = int(0.45 * sample_rate)
        tt = np.arange(length) / sample_rate
        horn = np.sin(2 * np.pi * 430 * tt) + 0.5 * np.sin(2 * np.pi * 540 * tt)
        env = dsp.adsr(length, attack=0.03, decay=0.05, sustain=0.8, release=0.15,
                       sample_rate=sample_rate)
        out[start:start + length] += horn * env * 0.3
    return dsp.normalize_peak(out, 0.9).astype(np.float32)
