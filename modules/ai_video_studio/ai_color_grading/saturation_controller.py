"""Saturation controller — luma-preserving saturation adjustment."""
from __future__ import annotations

from typing import Any

import numpy as np

from modules.ai_video_studio.ai_color_grading.grading_engine import to_float01
from modules.ai_video_studio.editor_common import make_logger

_LUMA = np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)

logger = make_logger("color.saturation")


class SaturationController:
    def apply(self, frame: Any, amount: float) -> np.ndarray:
        """amount 0 = grayscale, 1 = unchanged, >1 = more saturated."""
        img = to_float01(frame)
        luma = img @ _LUMA
        out = luma[..., None] + (img - luma[..., None]) * amount
        return (np.clip(out, 0, 1) * 255.0).astype(np.uint8)

    def vibrance(self, frame: Any, amount: float) -> np.ndarray:
        """Vibrance: boost mostly low-saturation pixels (keeps skin safe)."""
        from modules.ai_video_studio.ai_color_grading.skin_tone_optimizer import _hue_sat

        img = to_float01(frame)
        luma = img @ _LUMA
        _, sat = _hue_sat(img)
        per_pixel = 1.0 + amount * (1.0 - sat)[..., None]
        out = luma[..., None] + (img - luma[..., None]) * per_pixel
        return (np.clip(out, 0, 1) * 255.0).astype(np.uint8)
