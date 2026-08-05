"""Trumpet — brass-like odd harmonics with a punchy attack."""
from __future__ import annotations

import math

import numpy as np

from modules.ai_video_studio.media import dsp


def render(name: str, frequency: float, duration: float, *, amplitude: float = 0.45,
           sample_rate: int = dsp.SAMPLE_RATE) -> np.ndarray:
    n = int(duration * sample_rate)
    t = np.arange(n) / sample_rate
    sig = np.zeros(n, dtype=np.float64)
    for k in range(1, 8, 2):  # 1,3,5,7
        gain = 1.0 / (k ** 0.8)
        sig += gain * np.sin(2 * math.pi * frequency * k * t)
    sig /= np.max(np.abs(sig)) + 1e-9
    env = dsp.adsr(n, attack=0.02, decay=0.08, sustain=0.8, release=0.06, sample_rate=sample_rate)
    return (amplitude * sig * env).astype(np.float32)
