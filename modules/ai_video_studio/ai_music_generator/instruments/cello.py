"""Cello — bowed sawtooth in the low register with vibrato."""
from __future__ import annotations

import math

import numpy as np

from modules.ai_video_studio.media import dsp


def render(name: str, frequency: float, duration: float, *, amplitude: float = 0.4,
           sample_rate: int = dsp.SAMPLE_RATE) -> np.ndarray:
    n = int(duration * sample_rate)
    t = np.arange(n) / sample_rate
    vibrato = 1.0 + 0.005 * np.sin(2 * math.pi * 5.0 * t)
    phase = 2 * math.pi * frequency * np.cumsum(vibrato) / sample_rate
    saw = 2 * ((phase / (2 * math.pi)) % 1.0) - 1.0
    saw = dsp.one_pole_lp(saw, 1800.0, sample_rate=sample_rate)
    env = dsp.adsr(n, attack=0.1, decay=0.15, sustain=0.8, release=0.2, sample_rate=sample_rate)
    return (amplitude * saw * env).astype(np.float32)
