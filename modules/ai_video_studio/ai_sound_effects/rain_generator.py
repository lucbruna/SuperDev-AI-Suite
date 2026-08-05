"""Rain Generator — hiss bed plus random droplet ticks."""
from __future__ import annotations

import numpy as np

from modules.ai_video_studio.media import dsp


def generate(duration: float, *, sample_rate: int = dsp.SAMPLE_RATE, seed: int = 0,
             intensity: float = 0.6, **_: object) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = int(duration * sample_rate)
    bed = dsp.noise_white(duration, sample_rate=sample_rate, seed=seed)[:n]
    bed = dsp.one_pole_lp(bed, 2400.0, sample_rate=sample_rate)
    out = bed * intensity
    # Droplet transients.
    droplet_count = int(duration * (18 * intensity))
    for _ in range(droplet_count):
        start = int(rng.integers(0, n - 200))
        length = int(rng.integers(80, 260))
        tick = dsp.noise_white(length / sample_rate, sample_rate=sample_rate, seed=int(rng.integers(0, 9999)))[:length]
        tick = dsp.one_pole_hp(tick, 4000.0, sample_rate=sample_rate)
        out[start:start + length] += tick * rng.uniform(0.3, 0.8)
    return dsp.normalize_peak(out, 0.85).astype(np.float32)
