"""Guitar — Karplus-Strong plucked-string synthesis."""
from __future__ import annotations

import numpy as np

from modules.ai_video_studio.media import dsp


def render(name: str, frequency: float, duration: float, *, amplitude: float = 0.4,
           sample_rate: int = dsp.SAMPLE_RATE, pick: float = 0.6) -> np.ndarray:
    n = int(duration * sample_rate)
    delay = max(2, int(sample_rate / frequency))
    rng = np.random.default_rng(int(frequency) % 10000)
    buffer = rng.uniform(-1, 1, delay)
    buffer *= np.linspace(pick, 1.0, delay)  # pick direction shaping
    out = np.zeros(n, dtype=np.float64)
    for i in range(n):
        sample = buffer[0]
        buffer = np.roll(buffer, -1)
        buffer[-1] = 0.5 * (buffer[0] + sample) * 0.996
        out[i] = sample
    out = out / (np.max(np.abs(out)) + 1e-9)
    env = dsp.exp_decay(n, tau=duration * 0.5, sample_rate=sample_rate)
    return (amplitude * out * env).astype(np.float32)
