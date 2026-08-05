"""Object composition — place foreground objects on a background frame."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from .blending_modes import blend


def place_object(
    background: NDArray[np.floating],
    obj: NDArray[np.floating],
    *,
    x: int,
    y: int,
    scale: float = 1.0,
    alpha: float = 1.0,
    shadow: bool = True,
) -> NDArray[np.floating]:
    """Paste ``obj`` (RGB float) at (x, y) with optional soft drop shadow."""
    h, w = background.shape[:2]
    oh, ow = obj.shape[:2]
    if scale != 1.0:
        nh, nw = max(1, int(oh * scale)), max(1, int(ow * scale))
        from modules.ai_video_studio.editor_common import resize

        obj = resize(obj, nw, nh)
        oh, ow = obj.shape[:2]

    out = background.astype(np.float64).copy()
    if shadow:
        offset = max(2, min(oh, ow) // 20)
        for i in range(3, 0, -1):
            sx = x + offset - (3 - i) * max(1, offset // 2)
            sy = y + offset - (3 - i) * max(1, offset // 2)
            if sx + ow <= 0 or sy + oh <= 0 or sx >= w or sy >= h:
                continue
            x0, x1 = max(0, sx), min(w, sx + ow)
            y0, y1 = max(0, sy), min(h, sy + oh)
            ox0, oy0 = x0 - sx, y0 - sy
            patch = np.full((y1 - y0, x1 - x0, 3), 0.05)
            out[y0:y1, x0:x1] = blend(out[y0:y1, x0:x1], patch, mode="multiply")

    x0, x1 = max(0, x), min(w, x + ow)
    y0, y1 = max(0, y), min(h, y + oh)
    if x0 >= x1 or y0 >= y1:
        return out
    ox0, oy0 = x0 - x, y0 - y
    region = out[y0:y1, x0:x1]
    obj_patch = obj[oy0 : oy0 + (y1 - y0), ox0 : ox0 + (x1 - x0)]
    out[y0:y1, x0:x1] = blend(region, obj_patch, amount=alpha)
    return out
