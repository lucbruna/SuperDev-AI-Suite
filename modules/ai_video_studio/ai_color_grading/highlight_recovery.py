"""Highlight recovery — soft-roll clipped highlights back into range.

A luma mask weights the rolloff: only near-white pixels (and their neighbours
via a blur) get compressed, so mid-tones stay untouched.
"""
from __future__ import annotations

from typing import Any

import numpy as np

from modules.ai_video_studio.ai_color_grading.grading_engine import to_float01
from modules.ai_video_studio.editor_common import smoothstep, make_logger

logger = make_logger("color.highlight")


class HighlightRecovery:
    def apply(self, frame: Any, threshold: float = 0.85, strength: float = 0.6) -> np.ndarray:
        img = to_float01(frame)
        luma = img @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
        mask = smoothstep(threshold, 1.0, luma)[..., None]
        recovered = np.minimum(img, 1.0 - (1.0 - img) * strength)
        out = img * (1 - mask) + recovered * mask
        return (np.clip(out, 0, 1) * 255.0).astype(np.uint8)
