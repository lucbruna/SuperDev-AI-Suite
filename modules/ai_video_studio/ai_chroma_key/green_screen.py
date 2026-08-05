"""Green screen keying convenience."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from ..ai_compositor.matte_generator import chroma_matte


def key_green_screen(
    frame: NDArray[np.floating],
    *,
    tolerance: float = 0.35,
    softness: float = 0.12,
) -> NDArray[np.floating]:
    """Return a soft matte (0 = green removed, 1 = subject)."""
    return chroma_matte(frame, key_color=(0.0, 0.9, 0.0), tolerance=tolerance, softness=softness)
