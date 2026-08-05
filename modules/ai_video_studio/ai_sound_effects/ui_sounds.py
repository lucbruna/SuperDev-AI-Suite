"""UI Sounds — short interface blips (click/tick/confirm/error)."""
from __future__ import annotations

import numpy as np

from modules.ai_video_studio.media import dsp


def generate(duration: float, *, sample_rate: int = dsp.SAMPLE_RATE, seed: int = 0,
             kind: str = "click", **_: object) -> np.ndarray:
    kind = kind.lower()
    n = int(max(0.08, duration) * sample_rate)
    t = np.arange(n) / sample_rate
    if kind == "confirm":
        sig = np.sin(2 * np.pi * 660 * t) * np.exp(-t * 18)
        sig += np.sin(2 * np.pi * 880 * t) * np.exp(-t * 18)
    elif kind == "error":
        sig = np.sin(2 * np.pi * 180 * t) * np.exp(-t * 10)
        sig += np.sin(2 * np.pi * 230 * t) * np.exp(-t * 10)
    elif kind == "tick":
        sig = np.sin(2 * np.pi * 1200 * t) * np.exp(-t * 60)
    else:  # click
        sig = dsp.noise_white(n / sample_rate, sample_rate=sample_rate, seed=seed)[:n]
        sig = dsp.one_pole_hp(sig, 1500.0, sample_rate=sample_rate) * np.exp(-t * 40)
    return dsp.normalize_peak(sig, 0.8).astype(np.float32)
