"""Sparks — bright additive spark particles bursting outward."""
from __future__ import annotations

from typing import Any

import numpy as np

from modules.ai_video_studio.ai_effects.effects_engine import draw_particles
from modules.ai_video_studio.editor_common import as_rgb, clamp, make_logger

logger = make_logger("effects.sparks")


def apply(frame: Any, params: dict[str, Any]) -> np.ndarray:
    img = as_rgb(frame).astype(np.float32) / 255.0
    h, w = img.shape[:2]
    count = int(clamp(float(params.get("count", 80)), 0.0, 1000.0))
    seed = int(params.get("seed", 42)) + int(params.get("frame_index", 0))
    cx = float(params.get("origin_x", 0.5)) * w
    cy = float(params.get("origin_y", 0.5)) * h
    rng = np.random.default_rng(seed)
    sparks = np.zeros((count, 2), dtype=np.float32)
    for i in range(count):
        theta = rng.uniform(0, 2 * np.pi)
        speed = rng.uniform(0.1, 1.0) * 0.3 * max(w, h)
        sparks[i] = [cx + np.cos(theta) * speed, cy + np.sin(theta) * speed * 0.8]
    out = draw_particles(img, sparks, (1.0, 0.85, 0.5), radius=2, alpha=0.9, additive=True)
    return (out * 255).astype(np.uint8)
