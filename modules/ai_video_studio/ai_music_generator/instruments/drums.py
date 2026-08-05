"""Drums — real synthesis of a small drum kit."""
from __future__ import annotations

import math

import numpy as np

from modules.ai_video_studio.media import dsp

_KIT = {"kick", "snare", "hihat", "clap", "tom"}


def render(name: str, frequency: float, duration: float, *, amplitude: float = 0.7,
           sample_rate: int = dsp.SAMPLE_RATE) -> np.ndarray:
    """``name`` selects the drum (kick/snare/hihat/clap/tom)."""
    drum = name.lower()
    n = int(duration * sample_rate)
    if drum == "kick":
        return _kick(n, sample_rate) * amplitude
    if drum == "snare":
        return _snare(n, sample_rate) * amplitude
    if drum == "hihat":
        return _hihat(n, sample_rate) * amplitude
    if drum == "clap":
        return _clap(n, sample_rate) * amplitude
    if drum == "tom":
        return _tom(n, frequency, sample_rate) * amplitude
    return _kick(n, sample_rate) * amplitude


def _kick(n: int, sr: int) -> np.ndarray:
    t = np.arange(n) / sr
    freq = 120.0 * np.exp(-t * 12.0) + 40.0  # pitch drop
    phase = 2 * math.pi * np.cumsum(freq) / sr
    sig = np.sin(phase)
    env = np.exp(-t * 9.0)
    return (sig * env).astype(np.float32)


def _snare(n: int, sr: int) -> np.ndarray:
    t = np.arange(n) / sr
    tone = np.sin(2 * math.pi * 180 * t) * np.exp(-t * 25)
    noise = dsp.noise_white(n / sr, sample_rate=sr, seed=7)[:n]
    noise = dsp.biquad_peak(noise, 1800.0, 1.0, 6.0, sample_rate=sr) * np.exp(-t * 30)
    return ((tone * 0.6 + noise * 0.5) * (t < 0.25)).astype(np.float32)


def _hihat(n: int, sr: int) -> np.ndarray:
    t = np.arange(n) / sr
    noise = dsp.noise_white(n / sr, sample_rate=sr, seed=11)[:n]
    noise = dsp.one_pole_hp(noise, 7000.0, sample_rate=sr)
    return (noise * np.exp(-t * 60) * 0.7).astype(np.float32)


def _clap(n: int, sr: int) -> np.ndarray:
    t = np.arange(n) / sr
    noise = dsp.noise_white(n / sr, sample_rate=sr, seed=13)[:n]
    noise = dsp.biquad_peak(noise, 1200.0, 1.2, 4.0, sample_rate=sr)
    env = np.exp(-t * 18)
    return (noise * env * 0.8).astype(np.float32)


def _tom(n: int, frequency: float, sr: int) -> np.ndarray:
    freq = max(60.0, frequency or 110.0)
    t = np.arange(n) / sr
    sig = np.sin(2 * math.pi * freq * t) + 0.3 * np.sin(2 * math.pi * freq * 1.5 * t)
    env = np.exp(-t * 8.0)
    return (sig * env).astype(np.float32)


def is_drum(name: str) -> bool:
    return name.lower() in _KIT
