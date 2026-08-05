"""Frame interpolator — increase frame rate via interpolation."""
from __future__ import annotations

from typing import Any


class FrameInterpolator:
    """Creates intermediate frames between keyframes (blending)."""

    def interpolate(self, frames: list[dict[str, Any]], factor: int = 2) -> list[dict[str, Any]]:
        if factor <= 1:
            return list(frames)
        output: list[dict[str, Any]] = []
        for i in range(len(frames) - 1):
            a, b = frames[i], frames[i + 1]
            output.append(a)
            for step in range(1, factor):
                alpha = step / factor
                output.append(
                    {
                        "index": len(output),
                        "width": a["width"],
                        "height": a["height"],
                        "scene": a["scene"],
                        "style": a["style"],
                        "seed": (a["seed"] + b["seed"]) // 2,
                        "blend": round(alpha, 3),
                        "source": [a["index"], b["index"]],
                    }
                )
        output.append(frames[-1])
        return output
