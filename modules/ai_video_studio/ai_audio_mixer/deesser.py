"""De-esser — reduces harsh sibilance by ducking the 5-8 kHz band."""
from __future__ import annotations

import numpy as np

from modules.ai_video_studio.media import dsp


def deess(x: np.ndarray, *, threshold: float = 0.25, ratio: float = 0.4,
          sample_rate: int = dsp.SAMPLE_RATE) -> np.ndarray:
    """Split off the sibilance band, compress it, and blend back."""
    n = len(x)
    if n == 0:
        return x
    sibilance = dsp.biquad_peak(x, 6800.0, 0.9, 6.0, sample_rate=sample_rate)
    sibilance = dsp.biquad_peak(sibilance, 3400.0, 1.2, -8.0, sample_rate=sample_rate)
    # Envelope-detect and duck.
    env = np.abs(sibilance)
    at = np.exp(-1.0 / (0.002 * sample_rate))
    rt = np.exp(-1.0 / (0.05 * sample_rate))
    gain = np.ones(n)
    level = 0.0
    for i in range(n):
        if env[i] > level:  # noqa: SIM108 — clearer as a branch
            level = at * level + (1 - at) * env[i]
        else:
            level = rt * level + (1 - rt) * env[i]
        if level > threshold:
            gain[i] = 1.0 - (1.0 - ratio) * min(1.0, (level - threshold) / threshold)
        else:
            gain[i] = 1.0
    return (x - sibilance + sibilance * gain).astype(np.float32)
