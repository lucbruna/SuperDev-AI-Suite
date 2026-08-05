"""Shadow recovery — lift crushed shadows while preserving blacks.

The lift is weighted by a shadow mask (smoothstep near black) so pure blacks
stay black and only the near-black range opens up.
"""
from __future__ import annotations

from typing import Any

import numpy as np

from modules.ai_video_studio.ai_color_grading.grading_engine import to_float01
from modules.ai_video_studio.editor_common import smoothstep, make_logger

logger = make_logger("color.shadow")


class ShadowRecovery:
    def apply(self, frame: Any, amount: float = 0.15, preserve_black: float = 0.05) -> np.ndarray:
        img = to_float01(frame)
        luma = img @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
        mask = smoothstep(preserve_black, 0.5, luma)
        mask = 1.0 - mask  # strongest in the shadows
        out = img + amount * mask[..., None]
        return (np.clip(out, 0, 1) * 255.0).astype(np.uint8)
