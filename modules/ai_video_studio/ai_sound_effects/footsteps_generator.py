"""Footsteps Generator — rhythmic walking thuds."""
from __future__ import annotations

import numpy as np

from modules.ai_video_studio.media import dsp


def generate(duration: float, *, sample_rate: int = dsp.SAMPLE_RATE, seed: int = 0,
             steps_per_second: float = 2.0, surface: str = "ground", **_: object) -> np.ndarray:
    n = int(duration * sample_rate)
    out = np.zeros(n, dtype=np.float64)
    rng = np.random.default_rng(seed)
    interval = 1.0 / max(0.5, steps_per_second)
    t = 0.0
    while t < duration - 0.1:
        step_len = int(0.22 * sample_rate)
        start = int(t * sample_rate)
        if start + step_len <= n:
            thump = dsp.noise_brown(step_len / sample_rate, sample_rate=sample_rate,
                                    seed=int(rng.integers(0, 9999)))[:step_len]
            thump = dsp.one_pole_lp(thump, 300.0 if surface == "ground" else 900.0,
                                    sample_rate=sample_rate)
            thump *= np.exp(-np.arange(step_len) / (0.04 * sample_rate))
            thump += 0.5 * np.sin(2 * np.pi * 95 * np.arange(step_len) / sample_rate) * \
                np.exp(-np.arange(step_len) / (0.03 * sample_rate))
            out[start:start + step_len] += thump * rng.uniform(0.7, 1.0)
        t += interval * rng.uniform(0.92, 1.08)
    return dsp.normalize_peak(out, 0.85).astype(np.float32)
