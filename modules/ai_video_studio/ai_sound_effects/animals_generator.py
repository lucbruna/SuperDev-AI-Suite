"""Animals Generator — roars/growls (low sawtooth + noise)."""
from __future__ import annotations

import math

import numpy as np

from modules.ai_video_studio.media import dsp


def generate(duration: float, *, sample_rate: int = dsp.SAMPLE_RATE, seed: int = 0,
             kind: str = "roar", **_: object) -> np.ndarray:
    n = int(duration * sample_rate)
    t = np.arange(n) / sample_rate
    # Growl pitch wobble (menacing modulation).
    f0 = 70.0 if kind == "roar" else 55.0
    mod = 1.0 + 0.25 * np.sin(2 * math.pi * 3.0 * t + seed)
    phase = 2 * math.pi * f0 * np.cumsum(mod) / sample_rate
    saw = 2 * ((phase / (2 * math.pi)) % 1.0) - 1.0
    saw = dsp.one_pole_lp(saw, 350.0, sample_rate=sample_rate)
    growl = dsp.noise_brown(duration, sample_rate=sample_rate, seed=seed)[:n]
    growl = dsp.one_pole_lp(growl, 900.0, sample_rate=sample_rate)
    env = dsp.adsr(n, attack=0.08, decay=0.2, sustain=0.8, release=0.3, sample_rate=sample_rate)
    return ((saw * 0.8 + growl * 0.5) * env).astype(np.float32)
