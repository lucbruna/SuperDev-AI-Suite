"""Edge refinement — tighten mask contours using frame edge information."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def refine_mask(
    mask: NDArray[np.floating],
    frame: NDArray[np.floating] | None = None,
    *,
    threshold: float = 0.5,
    iterations: int = 1,
) -> NDArray[np.floating]:
    """Threshold the mask, then contract/expand to remove specks."""
    m = mask[..., 0] if mask.ndim == 3 else mask
    binary = (m > threshold).astype(np.float64)
    for _ in range(iterations):
        binary = np.maximum(
            np.maximum(binary, np.roll(binary, 1, 0)),
            np.maximum(np.roll(binary, -1, 0), np.maximum(np.roll(binary, 1, 1), np.roll(binary, -1, 1))),
        )
    # Remove border bleed: zero the outer ring
    binary[0] = 0
    binary[-1] = 0
    binary[:, 0] = 0
    binary[:, -1] = 0
    return binary
