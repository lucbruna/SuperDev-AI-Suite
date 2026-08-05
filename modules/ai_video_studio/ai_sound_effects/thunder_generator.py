"""Thunder Generator — sub rumble + initial crack."""
from __future__ import annotations

import numpy as np

from modules.ai_video_studio.media import dsp


def generate(duration: float, *, sample_rate: int = dsp.SAMPLE_RATE, seed: int = 0,
             intensity: float = 0.9, **_: object) -> np.ndarray:
    n = int(duration * sample_rate)
    crack_len = int(0.35 * sample_rate)
    crack = dsp.noise_white(crack_len / sample_rate, sample_rate=sample_rate, seed=seed)[:crack_len]
    crack = dsp.one_pole_hp(crack, 900.0, sample_rate=sample_rate)
    crack_env = dsp.exp_decay(crack_len, tau=0.06, sample_rate=sample_rate)
    rumble = dsp.noise_brown(duration, sample_rate=sample_rate, seed=seed + 1)[:n]
    rumble = dsp.one_pole_lp(rumble, 220.0, sample_rate=sample_rate)
    # Sub sine punch under the rumble.
    t = np.arange(n) / sample_rate
    sub = np.sin(2 * np.pi * 45 * t) * np.exp(-t * 2.0) * 0.6
    out = np.zeros(n, dtype=np.float64)
    out[:crack_len] += crack * crack_env * intensity
    out += rumble * np.exp(-t * 1.2) * intensity
    out += sub * intensity
    return dsp.normalize_peak(out, 0.95).astype(np.float32)
