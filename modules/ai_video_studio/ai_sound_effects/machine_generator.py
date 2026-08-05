"""Machine Generator — hum + periodic mechanical clatter."""
from __future__ import annotations

import numpy as np

from modules.ai_video_studio.media import dsp


def generate(duration: float, *, sample_rate: int = dsp.SAMPLE_RATE, seed: int = 0,
             cycle_hz: float = 1.4, **_: object) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = int(duration * sample_rate)
    t = np.arange(n) / sample_rate
    hum = np.sin(2 * np.pi * 120 * t) + 0.5 * np.sin(2 * np.pi * 240 * t)
    hum = dsp.one_pole_lp(hum, 1000.0, sample_rate=sample_rate) * 0.3
    out = hum.astype(np.float64)
    # Mechanical click each cycle.
    interval = 1.0 / max(0.2, cycle_hz)
    t_cursor = 0.0
    while t_cursor < duration - 0.05:
        start = int(t_cursor * sample_rate)
        length = int(0.05 * sample_rate)
        if start + length <= n:
            click = dsp.noise_white(length / sample_rate, sample_rate=sample_rate,
                                    seed=int(rng.integers(0, 9999)))[:length]
            click = dsp.biquad_peak(click, 1500.0, 1.0, 6.0, sample_rate=sample_rate)
            click = click * np.exp(-np.arange(length) / (0.008 * sample_rate))
            out[start:start + length] += click * 0.8
        t_cursor += interval
    return dsp.normalize_peak(out, 0.9).astype(np.float32)
