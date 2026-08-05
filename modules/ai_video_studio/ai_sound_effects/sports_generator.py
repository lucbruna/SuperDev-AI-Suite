"""Sports Generator — referee whistle + crowd bed."""
from __future__ import annotations

import numpy as np

from modules.ai_video_studio.media import dsp
from modules.ai_video_studio.ai_sound_effects.crowd_generator import generate as _crowd


def generate(duration: float, *, sample_rate: int = dsp.SAMPLE_RATE, seed: int = 0,
             whistles: int = 2, **_: object) -> np.ndarray:
    n = int(duration * sample_rate)
    rng = np.random.default_rng(seed)
    crowd = _crowd(duration, sample_rate=sample_rate, seed=seed, intensity=0.5) * 0.6
    out = crowd.astype(np.float64)
    # Whistle must fit between the low bound and the end — clamp for short
    # durations so ``low < high`` always holds (numpy.integers raises otherwise).
    low = int(0.4 * sample_rate)
    whistle_len = min(int(0.6 * sample_rate), max(1, n - low - 1))
    tt = np.arange(whistle_len) / sample_rate
    # Dual-tone referee whistle with trill.
    vibrato = 1.0 + 0.03 * np.sin(2 * np.pi * 18 * tt)
    whistle = np.sin(2 * np.pi * 2200 * tt * vibrato) + \
        0.6 * np.sin(2 * np.pi * 2900 * tt * vibrato)
    env = dsp.adsr(whistle_len, attack=0.03, decay=0.1, sustain=0.85, release=0.2,
                   sample_rate=sample_rate)
    for _ in range(max(1, whistles)):
        if n - whistle_len <= low:
            break
        start = int(rng.integers(low, n - whistle_len))
        out[start:start + whistle_len] += whistle * env * 0.5
    return dsp.normalize_peak(out, 0.9).astype(np.float32)
