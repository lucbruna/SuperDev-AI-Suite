"""Fire effect — rising embers with an orange-to-yellow core.

Embers are drawn additively so they brighten the scene; a second layer of
small yellow sparks sits near the core for the hot look.
"""
from __future__ import annotations

from typing import Any

import numpy as np

from modules.ai_video_studio.ai_effects.effects_engine import draw_particles
from modules.ai_video_studio.editor_common import as_rgb, clamp, make_logger

logger = make_logger("effects.fire")


def apply(frame: Any, params: dict[str, Any]) -> np.ndarray:
    img = as_rgb(frame).astype(np.float32) / 255.0
    h, w = img.shape[:2]
    intensity = clamp(float(params.get("intensity", 0.5)), 0.0, 1.0)
    origin_x = float(params.get("origin_x", 0.5)) * w
    origin_y = float(params.get("origin_y", 1.0)) * h
    seed = int(params.get("seed", 42)) + int(params.get("frame_index", 0))
    count = int(70 * intensity)
    rng = np.random.default_rng(seed)
    embers = np.zeros((count, 2), dtype=np.float32)
    for i in range(count):
        rise = rng.uniform(0.5, 2.0) * seed % (0.6 * h)
        sway = rng.uniform(-0.3, 0.3) * (seed % 40)
        embers[i] = [
            (origin_x + sway * rise) % w,
            (origin_y - rise) % h,
        ]
    out = draw_particles(img, embers, (1.0, 0.55, 0.15), radius=2, alpha=0.8, additive=True)
    sparks = embers[: count // 3]
    out = draw_particles(out, sparks, (1.0, 0.9, 0.4), radius=1, alpha=0.9, additive=True)
    return (out * 255).astype(np.uint8)
