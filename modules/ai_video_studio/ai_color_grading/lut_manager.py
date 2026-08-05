"""LUT manager — applies lookup tables to frames with an LRU cache.

LUTs are per-channel 1D tables (length 256 floats in [0, 1]). ``apply``
interpolates each channel through its table; results are cached per
(LUT id, frame hash) for repeated application in previews.
"""
from __future__ import annotations

import hashlib
from typing import Any

import numpy as np

from modules.ai_video_studio.ai_color_grading.grading_engine import to_float01
from modules.ai_video_studio.editor_common import make_logger

logger = make_logger("color.lut")


class LutManager:
    def __init__(self, cache_capacity: int = 128) -> None:
        self._cache: dict[tuple[str, str], np.ndarray] = {}
        self.capacity = cache_capacity

    def apply(self, lut_id: str, table: np.ndarray, frame: Any) -> np.ndarray:
        """Apply a 256-length 1D table (per channel or shared) to ``frame``."""
        table = np.asarray(table, dtype=np.float32)
        if table.shape[0] != 256:
            raise ValueError("LUT table must have 256 entries")
        if table.ndim == 1:
            table = np.stack([table] * 3, axis=-1)
        key = hashlib.sha1(frame.tobytes()).hexdigest()
        cache_key = (lut_id, key)
        if cache_key in self._cache:
            return self._cache[cache_key]
        img = to_float01(frame)
        x = (img * 255.0).astype(np.int32)
        x0 = np.clip(x, 0, 254)
        frac = (img * 255.0) - x0
        out = np.empty_like(img)
        for c in range(3):
            out[..., c] = table[x0[..., c], c] * (1 - frac[..., c]) + table[x0[..., c] + 1, c] * frac[..., c]
        result = (np.clip(out, 0, 1) * 255.0).astype(np.uint8)
        self._cache[cache_key] = result
        if len(self._cache) > self.capacity:
            self._cache.pop(next(iter(self._cache)))
        return result

    def clear(self) -> None:
        self._cache.clear()
