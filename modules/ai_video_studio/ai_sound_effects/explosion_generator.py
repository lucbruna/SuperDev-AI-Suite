"""Explosion Generator — blast + sub rumble tail."""
from __future__ import annotations

import numpy as np

from modules.ai_video_studio.media import dsp


def generate(duration: float, *, sample_rate: int = dsp.SAMPLE_RATE, seed: int = 0,
             intensity: float = 1.0, **_: object) -> np.ndarray:
    n = int(duration * sample_rate)
    t = np.arange(n) / sample_rate
    blast_len = int(min(0.4, duration * 0.4) * sample_rate)
    blast = dsp.noise_brown(blast_len / sample_rate, sample_rate=sample_rate, seed=seed)[:blast_len]
    blast = dsp.one_pole_hp(blast, 60.0, sample_rate=sample_rate)
    blast = blast * np.exp(-np.arange(blast_len) / (0.05 * sample_rate))

    rumble = dsp.noise_brown(duration, sample_rate=sample_rate, seed=seed + 3)[:n]
    rumble = dsp.one_pole_lp(rumble, 240.0, sample_rate=sample_rate)
    sub = np.sin(2 * np.pi * 42 * t) * np.exp(-t * 1.8)

    out = np.zeros(n, dtype=np.float64)
    out[:blast_len] += blast * intensity
    out += rumble * np.exp(-t * 1.4) * intensity * 0.8
    out += sub * intensity * 0.7
    return dsp.normalize_peak(out, 0.98).astype(np.float32)
