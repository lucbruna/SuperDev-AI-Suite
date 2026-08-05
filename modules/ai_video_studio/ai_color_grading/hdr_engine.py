"""HDR engine — exposure, tone mapping and range compression.

``tone_map`` applies a Reinhard curve (x / (1 + x)) to HDR-encoded luma so the
result fits the SDR [0, 1] range while preserving relative brightness.
``compress`` squeezes a log/float frame into display range with a soft rolloff.
"""
from __future__ import annotations

from typing import Any

import numpy as np

from modules.ai_video_studio.ai_color_grading.grading_engine import to_float01
from modules.ai_video_studio.editor_common import make_logger

logger = make_logger("color.hdr")


class HdrEngine:
    @staticmethod
    def tone_map(frame: Any, exposure: float = 0.0, key: float = 0.18) -> np.ndarray:
        """Reinhard tonemap on linear-exposure float input."""
        img = to_float01(frame).astype(np.float64) * (2.0 ** exposure)
        # Normalize by the luminance key to keep mid-grey stable.
        luma = img @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float64)
        scale = key / max(1e-6, float(luma.mean()))
        mapped = img * scale
        mapped = mapped / (1.0 + mapped)
        return (np.clip(mapped, 0, 1) * 255.0).astype(np.uint8)

    @staticmethod
    def compress(frame: Any, rolloff: float = 0.8) -> np.ndarray:
        """Soft-compress out-of-range values with a smooth rolloff."""
        img = to_float01(frame).astype(np.float64)
        clipped_hi = np.clip(img, 0.0, rolloff)
        excess = np.clip(img - rolloff, 0.0, 1.0)
        img = clipped_hi + excess * rolloff * 0.5
        return (np.clip(img, 0, 1) * 255.0).astype(np.uint8)

    @staticmethod
    def expand(frame: Any, stops: float) -> np.ndarray:
        """Expand SDR values into a wider range (2^stops multiplier)."""
        img = to_float01(frame).astype(np.float64) * (2.0 ** stops)
        return (np.clip(img, 0, 1) * 255.0).astype(np.uint8)

    def stats(self, frame: Any) -> dict[str, float]:
        img = to_float01(frame)
        return {
            "mean_luma": float((img @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)).mean()),
            "max": float(img.max()),
            "min": float(img.min()),
        }
