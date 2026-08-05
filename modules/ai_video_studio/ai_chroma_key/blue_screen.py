"""Blue screen keying convenience."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from ..ai_compositor.matte_generator import chroma_matte


def key_blue_screen(
    frame: NDArray[np.floating],
    *,
    tolerance: float = 0.35,
    softness: float = 0.12,
) -> NDArray[np.floating]:
    """Return a soft matte (0 = blue removed, 1 = subject)."""
    return chroma_matte(frame, key_color=(0.0, 0.3, 0.9), tolerance=tolerance, softness=softness)
