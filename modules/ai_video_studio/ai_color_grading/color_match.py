"""Color match — match one shot's colorimetry to a reference shot.

Uses per-channel mean/std matching in a soft-luma-preserving space so the
matched shot's overall exposure and color cast follow the reference.
"""
from __future__ import annotations

from typing import Any

import numpy as np

from modules.ai_video_studio.ai_color_grading.grading_engine import to_float01
from modules.ai_video_studio.editor_common import make_logger

logger = make_logger("color.match")


def _stats(img: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    pixels = img.reshape(-1, 3)
    return pixels.mean(axis=0), pixels.std(axis=0)


class ColorMatch:
    def match(self, reference: Any, target: Any) -> np.ndarray:
        """Match ``target`` toward ``reference`` and return the graded frame."""
        ref = to_float01(reference)
        tgt = to_float01(target)
        ref_mean, ref_std = _stats(ref)
        tgt_mean, tgt_std = _stats(tgt)
        out = (tgt - tgt_mean) / (tgt_std + 1e-6) * ref_std + ref_mean
        return (np.clip(out, 0, 1) * 255.0).astype(np.uint8)

    def gains(self, reference: Any, target: Any) -> dict[str, float]:
        """Return per-channel gain/offset so callers can apply it themselves."""
        ref_mean, ref_std = _stats(to_float01(reference))
        tgt_mean, tgt_std = _stats(to_float01(target))
        return {
            f"{ch}_gain": float(np.clip(ref_std[i] / max(1e-6, tgt_std[i]), 0.1, 10.0))
            for i, ch in enumerate(("r", "g", "b"))
        } | {
            f"{ch}_offset": float(ref_mean[i] - tgt_mean[i]) for i, ch in enumerate(("r", "g", "b"))
        }
