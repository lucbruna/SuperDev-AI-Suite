"""Snow effect — deterministic falling snowflakes with horizontal drift."""
from __future__ import annotations

from typing import Any

import numpy as np

from modules.ai_video_studio.ai_effects.effects_engine import draw_particles
from modules.ai_video_studio.editor_common import as_rgb, clamp, make_logger

logger = make_logger("effects.snow")


def apply(frame: Any, params: dict[str, Any]) -> np.ndarray:
    img = as_rgb(frame).astype(np.float32) / 255.0
    h, w = img.shape[:2]
    intensity = clamp(float(params.get("intensity", 0.5)), 0.0, 1.0)
    seed = int(params.get("seed", 42)) + int(params.get("frame_index", 0))
    count = int(140 * intensity)
    rng = np.random.default_rng(seed)
    flakes = np.zeros((count, 2), dtype=np.float32)
    for i in range(count):
        y = (rng.uniform(0, h) + seed * 0.7) % h
        drift = rng.uniform(-0.5, 0.5)
        x = (rng.uniform(0, w) + drift * seed) % w
        flakes[i] = [x, y]
    out = draw_particles(img, flakes, (1.0, 1.0, 1.0), radius=1.5, alpha=0.75, additive=True)
    return (out * 255).astype(np.uint8)
