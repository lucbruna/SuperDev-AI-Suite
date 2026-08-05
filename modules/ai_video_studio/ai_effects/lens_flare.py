"""Lens flare — procedural radial streaks and color ghosts.

Adds a bright streak from the source across the frame plus two colored ghost
discs, both attenuated by a radial falloff. Deterministic and fast.
"""
from __future__ import annotations

from typing import Any

import numpy as np

from modules.ai_video_studio.ai_effects.effects_engine import linear_dodge
from modules.ai_video_studio.editor_common import as_rgb, make_logger

logger = make_logger("effects.lensflare")


def apply(frame: Any, params: dict[str, Any]) -> np.ndarray:
    img = as_rgb(frame).astype(np.float32) / 255.0
    h, w = img.shape[:2]
    cx = float(params.get("x", 0.5)) * w
    cy = float(params.get("y", 0.5)) * h
    strength = float(params.get("strength", 0.5))
    color = np.array(params.get("color", [1.0, 0.9, 0.7]), dtype=np.float32)

    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    dx, dy = xx - cx, yy - cy
    dist = np.sqrt(dx * dx + dy * dy)
    falloff = np.exp(-dist / (0.35 * max(w, h)))

    # Horizontal streak.
    streak = np.exp(-np.abs(dy) / (0.02 * h)) * np.exp(-np.abs(dx) / (0.9 * w))
    # Two ghost discs on the opposite side of the frame.
    ghost1 = np.exp(-((xx - (cx + w * 0.18)) ** 2 + (yy - (cy + h * 0.02)) ** 2) / (2 * (0.05 * w) ** 2))
    ghost2 = np.exp(-((xx - (cx - w * 0.12)) ** 2 + (yy - (cy + h * 0.04)) ** 2) / (2 * (0.03 * w) ** 2))

    flare = (falloff * (0.6 * streak + 0.35 * ghost1 + 0.5 * ghost2)) * strength
    img = linear_dodge(img, color[None, None, :] * flare[..., None])
    return (np.clip(img, 0, 1) * 255).astype(np.uint8)
