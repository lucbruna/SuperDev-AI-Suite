"""Piano — harmonics + exponential decay + stereo detune."""
from __future__ import annotations

import math

import numpy as np

from modules.ai_video_studio.media import dsp

_HARMONICS = [(1.0, 1.0), (2.0, 0.45), (3.0, 0.22), (4.0, 0.12), (5.0, 0.06), (6.0, 0.03)]


def render(name: str, frequency: float, duration: float, *, amplitude: float = 0.4,
           sample_rate: int = dsp.SAMPLE_RATE) -> np.ndarray:
    n = int(duration * sample_rate)
    t = np.arange(n) / sample_rate
    sig = np.zeros(n, dtype=np.float64)
    for mult, gain in _HARMONICS:
        sig += gain * np.sin(2 * math.pi * frequency * mult * t)
    sig += 0.05 * np.sin(2 * math.pi * frequency * 0.997 * t)  # subtle detune
    env = np.exp(-t / max(0.25, duration * 0.35))
    env[: int(0.002 * sample_rate)] *= np.linspace(0, 1, int(0.002 * sample_rate))
    return (amplitude * sig * env).astype(np.float32)
