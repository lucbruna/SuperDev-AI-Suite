"""Rolling shutter correction — per-row horizontal shift compensation."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def fix_rolling_shutter(
    frame: NDArray[np.floating],
    *,
    vertical_speed: float = 0.0,
    sensitivity: float = 0.5,
) -> NDArray[np.floating]:
    """Correct horizontal skew caused by fast vertical motion.

    Rows are shifted progressively; ``vertical_speed`` is the frame's
    vertical displacement per readout time.
    """
    f = frame.astype(np.float64)
    h, w = f.shape[:2]
    max_shift = int(round(abs(vertical_speed) * sensitivity))
    if max_shift == 0:
        return f
    sign = 1 if vertical_speed > 0 else -1
    out = np.zeros_like(f)
    yy = np.arange(h)
    shift = (yy / max(1, h - 1) * max_shift * sign).astype(int)
    for i in range(h):
        out[i] = np.roll(f[i], -shift[i], axis=0)
    return out
