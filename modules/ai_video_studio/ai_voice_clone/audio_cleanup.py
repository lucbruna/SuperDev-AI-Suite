"""Audio Cleanup — prepares raw samples for cloning (trim/normalize/fade)."""
from __future__ import annotations

import numpy as np

from modules.ai_video_studio.media import dsp


def trim_silence(audio: np.ndarray, *, sample_rate: int = dsp.SAMPLE_RATE,
                 threshold: float = 0.005, margin: float = 0.15) -> np.ndarray:
    """Trim leading/trailing silence, keeping a small margin."""
    n = len(audio)
    if n < sample_rate:
        return audio
    frame = sample_rate // 20
    energies = []
    for start in range(0, n - frame, frame):
        energies.append(float(np.sum(audio[start:start + frame] ** 2)))
    if not energies:
        return audio
    active = np.asarray(energies) > threshold ** 2
    if not active.any():
        return audio[:1]
    first = int(np.argmax(active) * frame)
    last = int((len(active) - np.argmax(active[::-1]) - 1) * frame) + frame
    margin_samples = int(margin * sample_rate)
    return audio[max(0, first - margin_samples): min(n, last + margin_samples)]


def cleanup_sample(audio: np.ndarray, *, sample_rate: int = dsp.SAMPLE_RATE) -> np.ndarray:
    """Full cleanup pipeline for a raw voice recording."""
    out = trim_silence(audio, sample_rate=sample_rate)
    out = dsp.normalize_peak(out, 0.95)
    return dsp.fade_io(out, fade_in=0.01, fade_out=0.03, sample_rate=sample_rate)
