"""Violin — sawtooth with vibrato and bow noise."""
from __future__ import annotations

import math

import numpy as np

from modules.ai_video_studio.media import dsp


def render(name: str, frequency: float, duration: float, *, amplitude: float = 0.35,
           sample_rate: int = dsp.SAMPLE_RATE, vibrato_depth: float = 0.006) -> np.ndarray:
    n = int(duration * sample_rate)
    t = np.arange(n) / sample_rate
    vibrato = 1.0 + vibrato_depth * np.sin(2 * math.pi * 5.5 * t)
    phase = 2 * math.pi * frequency * np.cumsum(vibrato) / sample_rate
    sig = (2 * ((phase / (2 * math.pi)) % 1.0) - 1.0)  # saw
    # Tone it down with a gentle low-pass and add bow scratch.
    sig = dsp.one_pole_lp(sig, 3200.0, sample_rate=sample_rate)
    bow = dsp.noise_white(duration, sample_rate=sample_rate, seed=int(frequency) % 997)[:n]
    bow = dsp.one_pole_hp(bow, 4000.0, sample_rate=sample_rate) * 0.05
    env = dsp.adsr(n, attack=0.06, decay=0.1, sustain=0.75, release=0.15, sample_rate=sample_rate)
    return ((amplitude * sig + bow) * env).astype(np.float32)
