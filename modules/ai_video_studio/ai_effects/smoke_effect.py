"""Smoke effect — soft drifting smoke (alpha-blended grey blobs).

Unlike light effects, smoke uses alpha blending (non-additive) with large
soft discs so it darkens/lightens the scene naturally.
"""
from __future__ import annotations

from typing import Any

import numpy as np

from modules.ai_video_studio.ai_effects.effects_engine import draw_particles
from modules.ai_video_studio.editor_common import as_rgb, clamp, make_logger

logger = make_logger("effects.smoke")


def apply(frame: Any, params: dict[str, Any]) -> np.ndarray:
    img = as_rgb(frame).astype(np.float32) / 255.0
    h, w = img.shape[:2]
    density = clamp(float(params.get("density", 0.4)), 0.0, 1.0)
    seed = int(params.get("seed", 42)) + int(params.get("frame_index", 0))
    count = int(40 * density)
    rng = np.random.default_rng(seed)
    puffs = np.zeros((count, 2), dtype=np.float32)
    for i in range(count):
        y = (rng.uniform(0.3, 0.9) * h + seed * 1.1) % h
        x = (rng.uniform(0, w) + seed * 0.5) % w
        puffs[i] = [x, y]
    grey = np.array([0.55, 0.55, 0.6])
    out = draw_particles(img, puffs, (grey[0], grey[1], grey[2]), radius=6, alpha=0.18, additive=False)
    return (out * 255).astype(np.uint8)
