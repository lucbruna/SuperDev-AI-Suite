"""Hair refinement — soft-edge recovery around fine detail (hair, fur)."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def refine_hair(
    frame: NDArray[np.floating],
    matte: NDArray[np.floating],
    *,
    screen: str = "green",
    strength: float = 1.0,
) -> NDArray[np.floating]:
    """Boost matte detail in high-frequency edge areas.

    Uses local contrast of the screen channel: hair strands alternate
    between subject and screen color, producing high-frequency luminance.
    """
    channel = 1 if screen == "green" else 2
    detail = frame[..., channel]
    local_contrast = np.abs(detail - _box(detail, 3))
    edge_boost = np.clip(local_contrast * strength * 6, 0.0, 1.0)
    refined = matte + (1 - matte) * edge_boost * 0.5
    return np.clip(refined, 0.0, 1.0)


def _box(a: NDArray[np.floating], k: int) -> NDArray[np.floating]:
    pad = k // 2
    padded = np.pad(a, pad, mode="edge")
    cum = np.cumsum(padded, axis=0)
    out = (cum[k:] - cum[:-k]) / k
    cum = np.cumsum(out, axis=1)
    padded = np.pad(out, ((0, 0), (pad, pad)), mode="edge")
    out = (padded[:, k:] - padded[:, :-k]) / k
    return out
