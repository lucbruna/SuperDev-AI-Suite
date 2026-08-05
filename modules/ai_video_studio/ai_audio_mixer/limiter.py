"""Limiter — lookahead peak limiter to prevent clipping."""
from __future__ import annotations

import numpy as np

from modules.ai_video_studio.media import dsp


def limit(x: np.ndarray, *, threshold: float = 0.95, lookahead: float = 0.005,
          release: float = 0.08, sample_rate: int = dsp.SAMPLE_RATE) -> np.ndarray:
    """Limit peaks to ``threshold`` using a lookahead window."""
    n = len(x)
    if n == 0:
        return x
    look = max(1, int(lookahead * sample_rate))
    # Peak envelope with lookahead (max over the window ahead).
    env = np.abs(x.astype(np.float64))
    look_env = np.copy(env)
    for i in range(n - 1, -1, -1):
        end = min(n, i + look)
        look_env[i] = np.max(env[i:end])
    gain = np.minimum(1.0, threshold / (look_env + 1e-9))
    # Smooth release.
    rt = np.exp(-1.0 / (release * sample_rate))
    smoothed = np.ones(n)
    g = 1.0
    for i in range(n):
        if gain[i] < g:  # noqa: SIM108 — clearer as a branch
            g = gain[i]
        else:
            g = rt * g + (1 - rt) * gain[i]
        smoothed[i] = g
    return (x * smoothed).astype(np.float32)
