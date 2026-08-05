"""Pitch Analyzer — fundamental frequency analysis over frames.

Real DSP: the signal is windowed and the f0 is estimated per frame with
autocorrelation, then summary statistics (mean, spread, vibrato) are derived.
"""
from __future__ import annotations

import numpy as np

from modules.ai_video_studio.media import dsp


def pitch_contour(audio: np.ndarray, *, sample_rate: int = dsp.SAMPLE_RATE,
                  frame: int = 2048, hop: int = 512) -> np.ndarray:
    """Per-frame f0 estimates (0 for unvoiced frames)."""
    n = len(audio)
    if n < frame:
        return np.array([dsp.f0_autocorr(audio, sample_rate=sample_rate)], dtype=np.float32)
    f0s: list[float] = []
    win = np.hanning(frame)
    for start in range(0, n - frame, hop):
        block = audio[start:start + frame] * win
        f0s.append(dsp.f0_autocorr(block, sample_rate=sample_rate))
    return np.asarray(f0s, dtype=np.float32)


def voiced_frames(audio: np.ndarray, *, sample_rate: int = dsp.SAMPLE_RATE) -> np.ndarray:
    """Only the frames where a reliable f0 was found."""
    contour = pitch_contour(audio, sample_rate=sample_rate)
    return contour[contour > 0]


def mean_f0(audio: np.ndarray, *, sample_rate: int = dsp.SAMPLE_RATE) -> float:
    voiced = voiced_frames(audio, sample_rate=sample_rate)
    return float(np.median(voiced)) if len(voiced) else 0.0


def f0_spread(audio: np.ndarray, *, sample_rate: int = dsp.SAMPLE_RATE) -> float:
    voiced = voiced_frames(audio, sample_rate=sample_rate)
    return float(np.std(voiced)) if len(voiced) > 1 else 0.0


def f0_range(audio: np.ndarray, *, sample_rate: int = dsp.SAMPLE_RATE) -> tuple[float, float]:
    voiced = voiced_frames(audio, sample_rate=sample_rate)
    if len(voiced) == 0:
        return (0.0, 0.0)
    return (float(voiced.min()), float(voiced.max()))


def vibrato_rate(audio: np.ndarray, *, sample_rate: int = dsp.SAMPLE_RATE,
                 frame: int = 1024, hop: int = 256) -> float:
    """Estimate vibrato (Hz) from periodic f0 modulation of sustained sound."""
    contour = pitch_contour(audio, sample_rate=sample_rate, frame=frame, hop=hop)
    voiced = contour[contour > 0]
    if len(voiced) < 40:
        return 0.0
    centred = voiced - voiced.mean()
    ac = np.correlate(centred, centred, mode="full")[len(centred) - 1:]
    ac /= ac[0] + 1e-9
    lag = 10
    peak_val = 0.0
    for i in range(10, min(len(ac) - 1, 200)):
        if ac[i] > peak_val:
            peak_val = ac[i]
            lag = i
    if peak_val < 0.3:
        return 0.0
    frame_rate = sample_rate / hop
    return frame_rate / lag
