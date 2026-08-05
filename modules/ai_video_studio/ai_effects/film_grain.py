"""Film grain — deterministic seeded grain overlay.

The noise is generated from ``params.seed + frame_index`` so grain is stable
across rerenders and animates smoothly across frames (each frame gets its own
noise sample, which is what makes it look like real film).
"""
from __future__ import annotations

from typing import Any

import numpy as np

from modules.ai_video_studio.editor_common import as_rgb, clamp, make_logger

logger = make_logger("effects.grain")


def apply(frame: Any, params: dict[str, Any]) -> np.ndarray:
    img = as_rgb(frame).astype(np.float32) / 255.0
    strength = clamp(float(params.get("strength", 0.06)), 0.0, 1.0)
    seed = int(params.get("seed", 42)) + int(params.get("frame_index", 0)) * 7919
    rng = np.random.default_rng(seed)
    noise = rng.normal(0.0, strength, size=img.shape).astype(np.float32)
    out = np.clip(img + noise, 0, 1)
    return (out * 255).astype(np.uint8)
