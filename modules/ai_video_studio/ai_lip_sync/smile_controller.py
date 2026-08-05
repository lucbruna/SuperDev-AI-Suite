"""Smile Controller — smile intensity from smile/wide visemes."""
from __future__ import annotations

from typing import Any


def smile_curve(timeline: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Per-frame smile intensity (0-1)."""
    out: list[dict[str, Any]] = []
    for f in timeline:
        viseme = f.get("viseme", "neutral")
        if viseme == "smile":
            value = 0.9
        elif viseme == "wide":
            value = 0.4
        elif viseme == "kiss":
            value = 0.2
        else:
            value = 0.0
        out.append({"frame": f.get("frame"), "time": f.get("time"), "value": value})
    return out
