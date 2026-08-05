"""Rain effect — deterministic falling rain streaks.

Drops fall with a slight wind angle; each frame advances the seeded droplet
positions, drawing thin bright streaks. Re-rendering with the same seed and
frame index yields identical frames.
"""
from __future__ import annotations

from typing import Any

import numpy as np

from modules.ai_video_studio.ai_effects.effects_engine import draw_particles
from modules.ai_video_studio.editor_common import as_rgb, clamp, make_logger

logger = make_logger("effects.rain")


def apply(frame: Any, params: dict[str, Any]) -> np.ndarray:
    img = as_rgb(frame).astype(np.float32) / 255.0
    h, w = img.shape[:2]
    intensity = clamp(float(params.get("intensity", 0.5)), 0.0, 1.0)
    angle = float(params.get("angle", 0.15))
    seed = int(params.get("seed", 42)) + int(params.get("frame_index", 0))
    count = int(120 * intensity)
    rng = np.random.default_rng(seed)
    drops = np.zeros((count, 2), dtype=np.float32)
    for i in range(count):
        y = rng.uniform(-h, h) + seed * 1.2 % (2 * h)
        x = rng.uniform(0, w)
        drops[i] = [x + y * angle, y]
        # Wrap vertically for continuity.
        drops[i, 1] = drops[i, 1] % (h + 20) - 10
        drops[i, 0] = drops[i, 0] % w
    out = draw_particles(img, drops, (0.7, 0.8, 1.0), radius=1.0, alpha=0.6, additive=True)
    return (out * 255).astype(np.uint8)
