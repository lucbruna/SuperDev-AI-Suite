"""Choir — several detuned sine voices with vowel formants."""
from __future__ import annotations

import math

import numpy as np

from modules.ai_video_studio.media import dsp

_VOICES = [(-0.04, 1.0), (0.0, 1.1), (0.05, 0.9), (0.09, 0.6)]  # (detune cents, gain)


def render(name: str, frequency: float, duration: float, *, amplitude: float = 0.4,
           sample_rate: int = dsp.SAMPLE_RATE) -> np.ndarray:
    n = int(duration * sample_rate)
    t = np.arange(n) / sample_rate
    sig = np.zeros(n, dtype=np.float64)
    for detune_cents, gain in _VOICES:
        f = frequency * 2 ** (detune_cents / 1200.0)
        sig += gain * np.sin(2 * math.pi * f * t + 0.3 * np.sin(2 * math.pi * 4.5 * t))
    # Soft formant colouring around 800 Hz (warm vowel).
    sig = dsp.biquad_peak(sig, 800.0, 0.8, 4.0, sample_rate=sample_rate)
    env = dsp.adsr(n, attack=0.15, decay=0.2, sustain=0.85, release=0.3, sample_rate=sample_rate)
    return (amplitude * sig / sum(g for _, g in _VOICES) * env).astype(np.float32)
