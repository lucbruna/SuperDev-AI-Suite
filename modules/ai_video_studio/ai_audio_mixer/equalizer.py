"""Equalizer — parametric biquad EQ with 3-band presets."""
from __future__ import annotations

import numpy as np

from modules.ai_video_studio.media import dsp

PRESETS = {
    "flat": [],
    "vocal": [(300.0, 0.0, 0.8), (3500.0, 3.0, 1.0), (200.0, -2.0, 0.8)],
    "telephone": [(300.0, 10.0, 1.5), (3400.0, 10.0, 1.5), (200.0, -12.0, 1.0), (6000.0, -12.0, 1.0)],
    "warm": [(250.0, 4.0, 0.9), (5000.0, -2.5, 1.0)],
    "bright": [(5000.0, 3.5, 1.0), (200.0, -1.5, 0.9)],
    "bass_boost": [(80.0, 6.0, 1.0), (200.0, 2.0, 1.0)],
}


def eq(x: np.ndarray, bands: list[tuple[float, float, float]], *,
       sample_rate: int = dsp.SAMPLE_RATE) -> np.ndarray:
    """Apply ``(freq, gain_db, q)`` biquad peak filters in series."""
    out = x.astype(np.float32)
    for freq, gain_db, q in bands:
        if abs(gain_db) < 0.05:
            continue
        out = dsp.biquad_peak(out, freq, max(0.3, q), gain_db, sample_rate=sample_rate)
    return out


def tone_controls(x: np.ndarray, *, bass_db: float = 0.0, mid_db: float = 0.0,
                  treble_db: float = 0.0, sample_rate: int = dsp.SAMPLE_RATE) -> np.ndarray:
    """3-band tone control (shelves + peak)."""
    out = x.astype(np.float32)
    if abs(bass_db) > 0.05:
        out = dsp.biquad_lowshelf(out, 250.0, bass_db, sample_rate=sample_rate)
    if abs(treble_db) > 0.05:
        out = dsp.biquad_highshelf(out, 5000.0, treble_db, sample_rate=sample_rate)
    if abs(mid_db) > 0.05:
        out = dsp.biquad_peak(out, 1200.0, 0.8, mid_db, sample_rate=sample_rate)
    return out


def apply_preset(x: np.ndarray, preset: str, *, sample_rate: int = dsp.SAMPLE_RATE) -> np.ndarray:
    return eq(x, PRESETS.get(preset, []), sample_rate=sample_rate)
