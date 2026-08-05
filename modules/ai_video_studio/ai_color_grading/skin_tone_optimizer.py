"""Skin tone optimizer — protect skin while adjusting saturation.

Builds a skin-weight mask from a hue band (warm hues) blended with a soft
saturation factor, then applies the saturation change only where the mask is
weak, keeping skin tones natural.
"""
from __future__ import annotations

from typing import Any

import numpy as np

from modules.ai_video_studio.ai_color_grading.grading_engine import to_float01
from modules.ai_video_studio.editor_common import make_logger

logger = make_logger("color.skin")


def _hue_sat(img: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mx = img.max(axis=-1)
    mn = img.min(axis=-1)
    diff = mx - mn
    sat = np.where(mx > 0, diff / np.maximum(mx, 1e-6), 0.0)
    hue = np.zeros_like(mx)
    r, g, b = img[..., 0], img[..., 1], img[..., 2]
    mask = diff > 1e-5
    rmask = mx == r
    gmask = mx == g
    hue = np.where(mask & rmask, 60.0 * (((g - b) / np.maximum(diff, 1e-6)) % 6.0), hue)
    hue = np.where(mask & gmask, 60.0 * (((b - r) / np.maximum(diff, 1e-6)) + 2.0), hue)
    hue = np.where(mask & ~rmask & ~gmask, 60.0 * (((r - g) / np.maximum(diff, 1e-6)) + 4.0), hue)
    return hue, sat


class SkinToneOptimizer:
    def skin_mask(self, frame: Any) -> np.ndarray:
        """Soft [0, 1] mask of skin-like pixels (warm hue + moderate sat)."""
        img = to_float01(frame)
        hue, sat = _hue_sat(img)
        warm = np.clip(1.0 - np.abs(hue - 30.0) / 40.0, 0.0, 1.0)
        sat_factor = np.clip(1.0 - np.abs(sat - 0.35) / 0.35, 0.0, 1.0)
        return warm * sat_factor

    def apply_saturation(self, frame: Any, amount: float, protect: float = 1.0) -> np.ndarray:
        """Saturate but keep skin tones (``protect`` 0..1 controls strength)."""
        img = to_float01(frame)
        luma = img @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
        skin = self.skin_mask(frame)[..., None]
        effective = amount * (1.0 - protect * skin)
        out = luma[..., None] + (img - luma[..., None]) * (1.0 + effective)
        return (np.clip(out, 0, 1) * 255.0).astype(np.uint8)
