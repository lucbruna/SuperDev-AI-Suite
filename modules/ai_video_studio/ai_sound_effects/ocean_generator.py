"""Ocean Generator — rolling waves from modulated brown noise."""
from __future__ import annotations

import numpy as np

from modules.ai_video_studio.media import dsp


def generate(duration: float, *, sample_rate: int = dsp.SAMPLE_RATE, seed: int = 0,
             intensity: float = 0.7, **_: object) -> np.ndarray:
    n = int(duration * sample_rate)
    t = np.arange(n) / sample_rate
    waves = dsp.noise_brown(duration, sample_rate=sample_rate, seed=seed)[:n]
    waves = dsp.one_pole_lp(waves, 600.0, sample_rate=sample_rate)
    # Wave swells at ~0.1 Hz with secondary ripple.
    lfo = 0.55 + 0.45 * np.sin(2 * np.pi * 0.1 * t + 1.3)
    lfo *= 0.8 + 0.2 * np.sin(2 * np.pi * 0.37 * t)
    # White hiss cresting with the waves.
    hiss = dsp.one_pole_hp(dsp.noise_white(duration, sample_rate=sample_rate, seed=seed + 2)[:n],
                           2000.0, sample_rate=sample_rate)
    return (waves * lfo * intensity + hiss * np.clip(lfo - 0.4, 0, 1) * 0.25 * intensity).astype(np.float32)
