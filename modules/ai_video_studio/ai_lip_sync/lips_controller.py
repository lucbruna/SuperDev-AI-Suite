"""Lips Controller — upper/lower lip separation from mouth openness."""
from __future__ import annotations

from typing import Any


def lip_separation(timeline: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Per-frame ``{upper_lip, lower_lip}`` (0-1) curves."""
    out: list[dict[str, Any]] = []
    for f in timeline:
        open_ = f.get("open", 0.0)
        out.append({
            "frame": f.get("frame"),
            "time": f.get("time"),
            "upper_lip": round(open_ * 0.45, 3),
            "lower_lip": round(open_ * 0.55, 3),
        })
    return out
