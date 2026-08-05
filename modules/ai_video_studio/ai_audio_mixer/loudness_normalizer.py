"""Loudness Normalizer — RMS/peak normalisation and loudness estimation."""
from __future__ import annotations

import numpy as np

from modules.ai_video_studio.media import dsp


def normalize(x: np.ndarray, *, target_rms: float = 0.2, target_peak: float = 0.95,
              apply_limiter: bool = True, sample_rate: int = dsp.SAMPLE_RATE) -> np.ndarray:
    """Normalize to target RMS then guard peaks (limiter when requested)."""
    out = dsp.normalize_rms(x, target_rms)
    if dsp.peak(out) > target_peak:
        out = dsp.normalize_peak(out, target_peak)
    if apply_limiter:
        out = dsp.limiter(out, min(0.98, target_peak + 0.03), sample_rate=sample_rate)
    return out.astype(np.float32)


def estimate_loudness(x: np.ndarray, *, sample_rate: int = dsp.SAMPLE_RATE) -> dict:
    """Simple loudness metrics (dBFS RMS, peak, crest factor)."""
    if len(x) == 0:
        return {"rms_db": -inf_guard(), "peak_db": -inf_guard(), "crest_db": 0.0}
    rms_db = 20 * np.log10(dsp.rms(x) + 1e-12)
    peak_db = 20 * np.log10(dsp.peak(x) + 1e-12)
    return {
        "rms_db": round(float(rms_db), 2),
        "peak_db": round(float(peak_db), 2),
        "crest_db": round(float(peak_db - rms_db), 2),
    }


def inf_guard() -> float:
    return -120.0
