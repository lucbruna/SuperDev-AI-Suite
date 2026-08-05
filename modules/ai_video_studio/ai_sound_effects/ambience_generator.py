"""Ambience Generator — soft wind/room-tone bed."""
from __future__ import annotations

import numpy as np

from modules.ai_video_studio.media import dsp


def generate(duration: float, *, sample_rate: int = dsp.SAMPLE_RATE, seed: int = 0,
             intensity: float = 0.5, **_: object) -> np.ndarray:
    n = int(duration * sample_rate)
    wind = dsp.noise_brown(duration, sample_rate=sample_rate, seed=seed)[:n]
    wind = dsp.one_pole_lp(wind, 400.0, sample_rate=sample_rate)
    # Slow swell LFO.
    t = np.arange(n) / sample_rate
    lfo = 0.6 + 0.4 * np.sin(2 * np.pi * 0.08 * t + seed)
    return (wind * lfo * intensity).astype(np.float32)
