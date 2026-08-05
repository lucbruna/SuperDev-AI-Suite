"""Chromatic aberration — radial shift of the red and blue channels.

Simulates lens fringing: red is pushed outward from the center, blue inward.
``amount`` is in pixels at the frame edge (0 disables).
"""
from __future__ import annotations

from typing import Any

import numpy as np

from modules.ai_video_studio.editor_common import as_rgb, make_logger

logger = make_logger("effects.chroma_aberration")


def apply(frame: Any, params: dict[str, Any]) -> np.ndarray:
    img = as_rgb(frame).astype(np.float32) / 255.0
    amount = max(0.0, float(params.get("amount", 2.0)))
    if amount <= 0:
        return as_rgb(frame)
    h, w = img.shape[:2]
    cy, cx = h / 2, w / 2
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    dx, dy = (xx - cx) / cx, (yy - cy) / cy
    dist = np.sqrt(dx * dx + dy * dy)
    scale = np.clip(dist, 0.0, 1.0) * amount

    # Vectorised sampling: channel[sy, sx] with clamped index grids.
    def _shift(channel: np.ndarray, offset: np.ndarray) -> np.ndarray:
        sy = np.clip(yy + offset * 0.6, 0, h - 1).astype(np.int32)
        sx = np.clip(xx + offset, 0, w - 1).astype(np.int32)
        return channel[sy, sx]

    out = img.copy()
    out[..., 0] = _shift(img[..., 0], scale)
    out[..., 2] = _shift(img[..., 2], -scale * 0.6)
    return (np.clip(out, 0, 1) * 255).astype(np.uint8)
