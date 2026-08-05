"""Transition Sounds — whooshes, risers and sweeps."""
from __future__ import annotations

import numpy as np

from modules.ai_video_studio.media import dsp


def generate(duration: float, *, sample_rate: int = dsp.SAMPLE_RATE, seed: int = 0,
             kind: str = "whoosh", **_: object) -> np.ndarray:
    kind = kind.lower()
    n = int(duration * sample_rate)
    t = np.arange(n) / sample_rate
    progress = t / max(t[-1], 1e-6)
    noise = dsp.noise_white(duration, sample_rate=sample_rate, seed=seed)[:n]
    noise = dsp.one_pole_hp(noise, 800.0, sample_rate=sample_rate)

    if kind in ("riser", "sweep_up"):
        # Bandpass center sweeps up → tension build.
        sweep = _bandpass_sweep(noise, 400.0, 6000.0, progress, sample_rate)
        env = progress ** 2
        if kind == "sweep_up":
            env = progress
    elif kind in ("impact", "boom"):
        sweep = noise * np.exp(-t * 6)
        sweep += np.sin(2 * np.pi * (60 + 40 * progress) * t) * np.exp(-t * 5)
        env = 1.0
    else:  # whoosh
        sweep = _bandpass_sweep(noise, 3000.0, 300.0, progress, sample_rate)
        env = np.sin(np.pi * progress)  # swells and decays
    return dsp.normalize_peak(sweep * env, 0.9).astype(np.float32)


def _bandpass_sweep(signal: np.ndarray, f_start: float, f_end: float,
                    progress: np.ndarray, sample_rate: int) -> np.ndarray:
    """Crude moving bandpass: multiply by a sine tuned to the sweep freq."""
    freq = f_start + (f_end - f_start) * progress
    phase = 2 * np.pi * np.cumsum(freq) / sample_rate
    carrier = np.sin(phase)
    return signal * carrier
