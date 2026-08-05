"""Background masks — everything that is not the subject."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def background_mask(subject_mask: NDArray[np.floating]) -> NDArray[np.floating]:
    """Invert a subject mask to select the background."""
    return 1.0 - np.clip(subject_mask, 0.0, 1.0)


def background_blur_mask(
    frame: NDArray[np.floating],
    subject_mask: NDArray[np.floating],
    *,
    falloff: float = 1.0,
) -> NDArray[np.floating]:
    """Mask that ramps up away from the subject (for depth-of-field comps)."""
    from ..ai_masks.feather_engine import feather

    m = 1.0 - np.clip(subject_mask, 0.0, 1.0)
    if falloff < 1.0:
        feather(m, 6)
        m = 1.0 - (1.0 - m) * (1.0 - falloff)
        m = np.clip(m, 0.0, 1.0)
    return m
