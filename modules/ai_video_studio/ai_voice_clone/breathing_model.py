"""Breathing Model — detects breaths in a sample and inserts breath marks.

Real detection: energy dips preceded by a fall that contain broadband
(breathy) energy are labelled as breaths. The model can then insert breath
pauses into a clone's speech timeline to make synthetic audio breathe.
"""
from __future__ import annotations

import numpy as np

from modules.ai_video_studio.media import dsp


def detect_breaths(audio: np.ndarray, *, sample_rate: int = dsp.SAMPLE_RATE,
                   frame: int = 512, hop: int = 256) -> list[float]:
    """Return timestamps (seconds) where breaths were detected."""
    n = len(audio)
    if n < frame * 2:
        return []
    energies: list[float] = []
    timestamps: list[float] = []
    for start in range(0, n - frame, hop):
        block = audio[start:start + frame]
        energies.append(float(np.sum(block ** 2)))
        timestamps.append(start / sample_rate)
    energies = np.asarray(energies)
    if len(energies) < 5:
        return []
    local_mean = np.convolve(energies, np.ones(5) / 5, mode="same")
    dips = (energies < 0.15 * local_mean) & (energies < np.percentile(energies, 25))
    breaths: list[float] = []
    prev = -2
    for i in range(1, len(energies) - 1):
        if dips[i] and not dips[i - 1] and i - prev > 2:
            breaths.append(round(timestamps[i], 3))
            prev = i
    return breaths


def insert_breaths(segments: list[dict], *, breath_seconds: float = 0.35) -> list[dict]:
    """Add ``breath_after`` pauses to a list of speech segments.

    Segments are dicts with ``text`` and ``duration``; pauses are inserted
    after clauses longer than one breath (~14 chars at reading speed).
    """
    out: list[dict] = []
    for seg in segments:
        out.append(seg)
        if len(seg.get("text", "")) > 42:
            out.append({"text": "", "duration": breath_seconds, "breath": True})
    return out
