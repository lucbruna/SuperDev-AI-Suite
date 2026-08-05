"""Dust particles — floating ambient dust motes (additive white).

Count controls how many motes; they drift slowly and wrap around the frame,
giving scenes a lived-in, volumetric feel.
"""
from __future__ import annotations

from typing import Any

import numpy as np

from modules.ai_video_studio.ai_effects.effects_engine import draw_particles
from modules.ai_video_studio.editor_common import as_rgb, clamp, make_logger

logger = make_logger("effects.dust")


def apply(frame: Any, params: dict[str, Any]) -> np.ndarray:
    img = as_rgb(frame).astype(np.float32) / 255.0
    h, w = img.shape[:2]
    count = int(clamp(float(params.get("count", 120)), 0.0, 2000.0))
    seed = int(params.get("seed", 42)) + int(params.get("frame_index", 0))
    rng = np.random.default_rng(seed)
    motes = np.zeros((count, 2), dtype=np.float32)
    for i in range(count):
        motes[i] = [
            (rng.uniform(0, w) + rng.uniform(-0.2, 0.2) * seed) % w,
            (rng.uniform(0, h) + rng.uniform(-0.1, 0.1) * seed) % h,
        ]
    out = draw_particles(img, motes, (1.0, 1.0, 0.95), radius=1, alpha=0.35, additive=True)
    return (out * 255).astype(np.uint8)
