"""Synthesizer — sawtooth/pulse with classic ADSR."""
from __future__ import annotations


import numpy as np

from modules.ai_video_studio.media import dsp


def render(name: str, frequency: float, duration: float, *, amplitude: float = 0.4,
           sample_rate: int = dsp.SAMPLE_RATE, pulse: float = 0.5) -> np.ndarray:
    n = int(duration * sample_rate)
    t = np.arange(n) / sample_rate
    phase = (frequency * t) % 1.0
    saw = 2 * phase - 1.0
    pulse_wave = np.where(phase < pulse, 1.0, -1.0)
    # Subtractive: darken the pulse for a softer pad.
    pulse_wave = dsp.one_pole_lp(pulse_wave, 2400.0, sample_rate=sample_rate)
    sig = 0.4 * saw + 0.6 * pulse_wave
    env = dsp.adsr(n, attack=0.02, decay=0.15, sustain=0.7, release=0.12, sample_rate=sample_rate)
    return (amplitude * sig * env).astype(np.float32)
