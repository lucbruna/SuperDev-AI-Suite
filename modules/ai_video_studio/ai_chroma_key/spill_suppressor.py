"""Spill suppression — pulls screen color out of subject edges."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def suppress_spill(
    frame: NDArray[np.floating],
    matte: NDArray[np.floating],
    *,
    key_color: tuple[float, float, float],
    amount: float = 0.5,
) -> NDArray[np.floating]:
    """Despill on the semi-transparent edge region (matte between 0 and 1)."""
    k = np.asarray(key_color, dtype=np.float64)
    edge = np.clip(matte, 0.0, 1.0)
    # Only where subject is partially present
    weight = edge * (1 - edge) * 4  # peak at 0.5
    spill = np.clip(frame[..., :3] - k, 0.0, None) * weight[..., None] * amount
    out = frame[..., :3] - spill
    return np.clip(out, 0.0, 1.0)
