"""Timbre Analyzer — spectral characterisation of a voice."""
from __future__ import annotations

import numpy as np

from modules.ai_video_studio.media import dsp

BANDS = {"bass": (0, 250), "low_mid": (250, 500), "mid": (500, 2000),
         "high_mid": (2000, 5000), "presence": (5000, 8000), "air": (8000, 16000)}


def analyze_timbre(audio: np.ndarray, *, sample_rate: int = dsp.SAMPLE_RATE) -> dict[str, float]:
    """Return spectral descriptors of a voice sample."""
    centroid = dsp.spectral_centroid(audio, sample_rate=sample_rate)
    rolloff = dsp.spectral_rolloff(audio, 0.85, sample_rate=sample_rate)
    brightness = dsp.spectral_rolloff(audio, 0.50, sample_rate=sample_rate)
    spec = np.abs(np.fft.rfft(audio))
    total = float(np.sum(spec)) + 1e-9
    bands: dict[str, float] = {}
    for name, (lo, hi) in BANDS.items():
        freqs = np.fft.rfftfreq(len(audio), 1.0 / sample_rate)
        mask = (freqs >= lo) & (freqs < hi)
        bands[name] = float(np.sum(spec[mask]) / total)
    return {
        "centroid_hz": round(centroid, 1),
        "rolloff_hz": round(rolloff, 1),
        "brightness_hz": round(brightness, 1),
        **{f"band_{name}": round(v, 4) for name, v in bands.items()},
    }


def timbre_profile(audio: np.ndarray, *, sample_rate: int = dsp.SAMPLE_RATE) -> dict[str, float]:
    """Compact timbre summary used for similarity comparisons."""
    analysis = analyze_timbre(audio, sample_rate=sample_rate)
    return {
        "centroid": analysis["centroid_hz"],
        "rolloff": analysis["rolloff_hz"],
        "brightness": analysis["brightness_hz"],
        "warmth": analysis["band_bass"] + analysis["band_low_mid"],
        "presence": analysis["band_high_mid"] + analysis["band_presence"],
    }
