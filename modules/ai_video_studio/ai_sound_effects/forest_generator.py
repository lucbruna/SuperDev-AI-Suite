"""Forest Generator — wind bed plus occasional bird chirps."""
from __future__ import annotations

import numpy as np

from modules.ai_video_studio.media import dsp
from modules.ai_video_studio.ai_sound_effects.birds_generator import generate as _birds


def generate(duration: float, *, sample_rate: int = dsp.SAMPLE_RATE, seed: int = 0,
             intensity: float = 0.6, **_: object) -> np.ndarray:
    n = int(duration * sample_rate)
    wind = dsp.noise_brown(duration, sample_rate=sample_rate, seed=seed)[:n]
    wind = dsp.one_pole_lp(wind, 500.0, sample_rate=sample_rate)
    t = np.arange(n) / sample_rate
    lfo = 0.6 + 0.4 * np.sin(2 * np.pi * 0.06 * t)
    out = wind * lfo * intensity * 0.5

    chirps = _birds(duration, sample_rate=sample_rate, seed=seed + 5, count=int(duration * 0.8))
    out = out + chirps * 0.5
    return dsp.normalize_peak(out, 0.9).astype(np.float32)
