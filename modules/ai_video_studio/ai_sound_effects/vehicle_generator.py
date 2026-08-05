"""Vehicle Generator — idling/accelerating engine."""
from __future__ import annotations

import numpy as np

from modules.ai_video_studio.media import dsp


def generate(duration: float, *, sample_rate: int = dsp.SAMPLE_RATE, seed: int = 0,
             rev: float = 0.4, **_: object) -> np.ndarray:
    n = int(duration * sample_rate)
    t = np.arange(n) / sample_rate
    # Engine RPM wobble; ``rev`` 0-1 raises the base speed.
    base = 35.0 + rev * 90.0
    rpm = base * (1.0 + 0.08 * np.sin(2 * np.pi * 2.3 * t))
    phase = 2 * np.pi * np.cumsum(rpm) / sample_rate
    engine = np.sin(phase) + 0.4 * np.sin(phase * 2) + 0.15 * np.sin(phase * 3)
    engine = dsp.one_pole_lp(engine, 900.0, sample_rate=sample_rate)
    exhaust = dsp.noise_brown(duration, sample_rate=sample_rate, seed=seed)[:n]
    exhaust = dsp.one_pole_lp(exhaust, 300.0, sample_rate=sample_rate) * 0.5
    out = engine * 0.8 + exhaust
    # Idle dips every ~1.2s.
    dip = 0.75 + 0.25 * np.sin(2 * np.pi * 0.83 * t + seed)
    return (out * dip).astype(np.float32)
