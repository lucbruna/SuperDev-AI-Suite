"""Vectorscope — U/V scatter data for hue & saturation inspection.

Converts RGB to a YUV-like space and returns downsampled U/V pairs plus the
count per bucket, which is what a vectorscope UI draws. Also exposes a simple
hue/saturation histogram.
"""
from __future__ import annotations

from typing import Any

import numpy as np

from modules.ai_video_studio.ai_color_grading.grading_engine import to_float01
from modules.ai_video_studio.editor_common import make_logger

logger = make_logger("color.vectorscope")

# BT.601-ish YUV matrix (for scope display purposes).
_MAT = np.array(
    [[0.299, 0.587, 0.114], [-0.14713, -0.28886, 0.436], [0.615, -0.51499, -0.10001]],
    dtype=np.float32,
)


class ScopesVectorscope:
    def compute(self, frame: Any, sample: int = 20000, buckets: int = 48) -> dict[str, Any]:
        img = to_float01(frame)
        h, w = img.shape[:2]
        pixels = img.reshape(-1, 3)
        if len(pixels) > sample:
            idx = np.linspace(0, len(pixels) - 1, sample).astype(int)
            pixels = pixels[idx]
        yuv = pixels @ _MAT.T
        u = np.clip(yuv[:, 1], -0.5, 0.5)
        v = np.clip(yuv[:, 2], -0.5, 0.5)
        hist, _, _ = np.histogram2d(u, v, bins=buckets, range=[[-0.5, 0.5], [-0.5, 0.5]])
        return {
            "buckets": buckets,
            "count": int(len(pixels)),
            "u": u.tolist(),
            "v": v.tolist(),
            "hist2d": hist.astype(int).tolist(),
        }

    def hue_saturation_hist(self, frame: Any, bins: int = 64) -> dict[str, Any]:
        from modules.ai_video_studio.ai_color_grading.skin_tone_optimizer import _hue_sat

        img = to_float01(frame)
        hue, sat = _hue_sat(img)
        hist_hue, _ = np.histogram(hue, bins=bins, range=(0.0, 360.0))
        hist_sat, _ = np.histogram(sat, bins=bins, range=(0.0, 1.0))
        return {"hue": hist_hue.tolist(), "saturation": hist_sat.tolist(), "bins": bins}
