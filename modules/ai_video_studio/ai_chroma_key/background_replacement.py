"""Background replacement — composite subject over a new background."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def replace_background(
    frame: NDArray[np.floating],
    matte: NDArray[np.floating],
    background: NDArray[np.floating],
) -> NDArray[np.floating]:
    """Composite ``frame`` over ``background`` using a soft ``matte``.

    The matte is interpreted as subject-opacity (1 = subject, 0 = background).
    """
    m = matte[..., None] if matte.ndim == 2 else matte[..., :1]
    m = np.clip(m, 0.0, 1.0)
    bg = background
    if bg.shape[:2] != frame.shape[:2]:
        from modules.ai_video_studio.editor_common import resize

        bg = resize(bg, frame.shape[1], frame.shape[0])
    return np.clip(frame[..., :3] * m + bg[..., :3] * (1 - m), 0.0, 1.0)
