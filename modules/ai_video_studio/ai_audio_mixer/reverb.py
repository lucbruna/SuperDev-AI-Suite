"""Reverb — Schroeder/Moorer style reverberator.

Four parallel comb filters feeding two series allpass filters — the classic
real-time reverb architecture, implemented sample-by-sample.
"""
from __future__ import annotations

import numpy as np

from modules.ai_video_studio.media import dsp

# Classic Schroeder tuning (delays in ms, feedback values).
_COMBS = [(29.7, 0.773), (37.1, 0.802), (41.1, 0.753), (43.7, 0.733)]
_ALLPASSES = [(5.0, 0.7), (1.7, 0.7)]


def reverb(x: np.ndarray, *, mix: float = 0.3, room_size: float = 1.0,
           damping: float = 0.85, sample_rate: int = dsp.SAMPLE_RATE) -> np.ndarray:
    """Add reverberation; ``mix`` 0-1 wet ratio."""
    if mix <= 0:
        return x.copy()
    wet = np.zeros_like(x, dtype=np.float64)
    for delay_ms, fb in _COMBS:
        delay_s = delay_ms / 1000.0 * room_size
        comb = dsp.comb(x, delay_s, fb * (0.6 + 0.4 * damping), sample_rate=sample_rate)
        wet += comb
    wet /= len(_COMBS)
    for delay_ms, fb in _ALLPASSES:
        wet = dsp.allpass(wet, delay_ms / 1000.0 * room_size, fb, sample_rate=sample_rate)
    wet = dsp.one_pole_lp(wet, 6500.0, sample_rate=sample_rate)
    wet = dsp.normalize_peak(wet, dsp.peak(x) + 1e-9) * 0.9
    return ((1 - mix) * x + mix * wet).astype(np.float32)
