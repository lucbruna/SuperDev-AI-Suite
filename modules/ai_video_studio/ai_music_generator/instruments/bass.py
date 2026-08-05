"""Bass — warm low-end (sine + soft saw) with decay."""
from __future__ import annotations

import math

import numpy as np

from modules.ai_video_studio.media import dsp


def render(name: str, frequency: float, duration: float, *, amplitude: float = 0.5,
           sample_rate: int = dsp.SAMPLE_RATE) -> np.ndarray:
    n = int(duration * sample_rate)
    t = np.arange(n) / sample_rate
    sine = np.sin(2 * math.pi * frequency * t)
    saw = 2 * ((frequency * t) % 1.0) - 1.0
    sig = sine + 0.25 * saw
    sig = dsp.one_pole_lp(sig, 900.0, sample_rate=sample_rate)
    env = dsp.adsr(n, attack=0.005, decay=0.2, sustain=0.6, release=0.08, sample_rate=sample_rate)
    return (amplitude * sig * env).astype(np.float32)
