"""Flute — airy sine with vibrato and breath."""
from __future__ import annotations

import math

import numpy as np

from modules.ai_video_studio.media import dsp


def render(name: str, frequency: float, duration: float, *, amplitude: float = 0.4,
           sample_rate: int = dsp.SAMPLE_RATE) -> np.ndarray:
    n = int(duration * sample_rate)
    t = np.arange(n) / sample_rate
    vibrato = 1.0 + 0.004 * np.sin(2 * math.pi * 5.0 * t)
    sig = np.sin(2 * math.pi * frequency * np.cumsum(vibrato) / sample_rate)
    breath = dsp.noise_white(duration, sample_rate=sample_rate, seed=23)[:n]
    breath = dsp.one_pole_hp(breath, 3500.0, sample_rate=sample_rate) * 0.04
    env = dsp.adsr(n, attack=0.08, decay=0.05, sustain=0.85, release=0.1, sample_rate=sample_rate)
    return ((amplitude * sig + breath) * env).astype(np.float32)
