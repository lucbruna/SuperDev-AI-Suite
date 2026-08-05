"""LUT library — built-in preset lookup tables.

Each preset is a 256×3 float table in [0, 1]. LUTs are computed analytically
(no assets needed) so they are deterministic and always available.
"""
from __future__ import annotations

from typing import Any

import numpy as np

from modules.ai_video_studio.editor_common import make_logger

logger = make_logger("color.lutlib")


def _channel(func: Any) -> np.ndarray:
    x = np.linspace(0.0, 1.0, 256, dtype=np.float32)
    return np.clip(func(x), 0.0, 1.0)


class LutLibrary:
    _PRESETS: dict[str, tuple[Any, Any, Any]] = {
        "neutral": (lambda x: x, lambda x: x, lambda x: x),
        "cinema": (lambda x: x ** 0.9, lambda x: x ** 1.0, lambda x: x ** 1.05),
        "fade": (lambda x: 0.08 + 0.92 * x, lambda x: 0.05 + 0.95 * x, lambda x: 0.06 + 0.94 * x),
        "bw": (lambda x: x, lambda x: x, lambda x: x),
        "teal": (lambda x: 0.97 * x + 0.03, lambda x: x ** 1.02, lambda x: 1.05 * x - 0.05),
        "warm": (lambda x: 1.04 * x - 0.02, lambda x: x, lambda x: 0.96 * x),
    }

    def table(self, name: str) -> np.ndarray:
        if name not in self._PRESETS:
            raise KeyError(f"Unknown LUT '{name}' (available: {', '.join(sorted(self._PRESETS))})")
        r, g, b = self._PRESETS[name]
        table = np.stack([_channel(r), _channel(g), _channel(b)], axis=-1)
        if name == "bw":
            luma = table @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
            table = np.stack([luma] * 3, axis=-1)
        return table

    def names(self) -> list[str]:
        return sorted(self._PRESETS)
