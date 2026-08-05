"""Frame reconstruction — synthesize missing frames by interpolation."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def reconstruct_frame(
    prev: NDArray[np.floating],
    next_: NDArray[np.floating],
    *,
    alpha: float = 0.5,
) -> NDArray[np.floating]:
    """Blend two frames to reconstruct a missing one in between."""
    return np.clip(prev * (1 - alpha) + next_ * alpha, 0.0, 1.0)


def fill_gaps(frames: list[NDArray[np.floating] | None]) -> list[NDArray[np.floating]]:
    """Replace None gaps with interpolation of the nearest valid neighbors."""
    out: list[NDArray[np.floating]] = []
    n = len(frames)
    for i, f in enumerate(frames):
        if f is not None:
            out.append(f)
            continue
        # find nearest valid prev/next
        prev_i, next_i = i - 1, i + 1
        while prev_i >= 0 and frames[prev_i] is None:
            prev_i -= 1
        while next_i < n and frames[next_i] is None:
            next_i += 1
        if prev_i >= 0 and next_i < n:
            alpha = 0.5
            out.append(reconstruct_frame(frames[prev_i], frames[next_i], alpha=alpha))
        elif prev_i >= 0:
            out.append(frames[prev_i])
        elif next_i < n:
            out.append(frames[next_i])
        else:
            raise ValueError("cannot reconstruct: no valid frames")
    return out
