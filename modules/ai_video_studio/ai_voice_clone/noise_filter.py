"""Noise Filter — practical noise reduction for voice samples.

Real DSP chain: high-pass hum removal, spectral gate on quiet bins, and
optional band attenuation. Designed for voice, so it preserves the
3-8 kHz sibilance region.
"""
from __future__ import annotations

import numpy as np

from modules.ai_video_studio.media import dsp


def denoise(audio: np.ndarray, *, sample_rate: int = dsp.SAMPLE_RATE,
            gate_threshold: float = 0.02, hp_cutoff: float = 60.0) -> np.ndarray:
    """Clean a voice sample: hum removal + spectral gating."""
    out = audio.astype(np.float32)
    if hp_cutoff > 0:
        out = dsp.one_pole_hp(out, hp_cutoff, sample_rate=sample_rate)
    out = dsp.spectral_gate(out, threshold=gate_threshold, sample_rate=sample_rate)
    return out


def remove_hum(audio: np.ndarray, *, sample_rate: int = dsp.SAMPLE_RATE) -> np.ndarray:
    """Remove 50/60 Hz mains hum with a narrow notch (biquad peak cut)."""
    out = audio.astype(np.float32)
    for freq in (50.0, 60.0):
        out = dsp.biquad_peak(out, freq, 8.0, -30.0, sample_rate=sample_rate)
    return out


def sibilance_preserving_cleanup(audio: np.ndarray, *, sample_rate: int = dsp.SAMPLE_RATE) -> np.ndarray:
    """Gate without touching the high band where sibilance lives."""
    cleaned = dsp.spectral_gate(audio, threshold=0.015, sample_rate=sample_rate)
    highs = dsp.one_pole_hp(audio, 5000.0, sample_rate=sample_rate)
    return np.clip(cleaned + 0.25 * highs, -1.0, 1.0).astype(np.float32)
