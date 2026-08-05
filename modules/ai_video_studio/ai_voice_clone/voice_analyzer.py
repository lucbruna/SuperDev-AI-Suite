"""Voice Analyzer — extracts a full descriptor set from a voice sample.

The descriptors (duration, energy, pitch, timbre, quality) power voice
matching, cloning and quality validation. Every value is computed from the
actual audio with real DSP.
"""
from __future__ import annotations

from typing import Any

import numpy as np

from modules.ai_video_studio.media import dsp
from modules.ai_video_studio.ai_voice_clone.pitch_analyzer import mean_f0, f0_spread, f0_range, vibrato_rate
from modules.ai_video_studio.ai_voice_clone.timbre_analyzer import analyze_timbre


def analyze_audio(audio: np.ndarray, *, sample_rate: int = dsp.SAMPLE_RATE) -> dict[str, Any]:
    """Analyze an already-loaded mono sample."""
    duration = len(audio) / sample_rate
    lo, hi = f0_range(audio, sample_rate=sample_rate)
    return {
        "duration": round(duration, 3),
        "rms": round(dsp.rms(audio), 5),
        "peak": round(dsp.peak(audio), 5),
        "snr_db": round(_estimate_snr_db(audio), 2),
        "clipping": bool(dsp.peak(audio) >= 0.999),
        "f0_mean": round(mean_f0(audio, sample_rate=sample_rate), 1),
        "f0_std": round(f0_spread(audio, sample_rate=sample_rate), 1),
        "f0_min": round(lo, 1),
        "f0_max": round(hi, 1),
        "vibrato_hz": round(vibrato_rate(audio, sample_rate=sample_rate), 2),
        **analyze_timbre(audio, sample_rate=sample_rate),
    }


def analyze_file(path: str, *, sample_rate: int = dsp.SAMPLE_RATE) -> dict[str, Any]:
    """Analyze an audio file on disk."""
    audio, sr = dsp.read_audio(path, target_sr=sample_rate)
    result = analyze_audio(audio, sample_rate=sr)
    result["file"] = path
    result["sample_rate"] = sr
    return result


def _estimate_snr_db(audio: np.ndarray, *, frame: int = 1024, hop: int = 512) -> float:
    """Simple SNR estimate: ratio of loud-frame energy to quiet-frame energy."""
    n = len(audio)
    if n < frame:
        return 20.0
    energies: list[float] = []
    for start in range(0, n - frame, hop):
        energies.append(float(np.sum(audio[start:start + frame] ** 2)))
    if not energies:
        return 20.0
    energies = np.asarray(energies)
    signal = np.percentile(energies, 90)
    noise = np.percentile(energies, 10)
    if noise < 1e-12:
        return 60.0
    return float(10 * np.log10(signal / noise))
