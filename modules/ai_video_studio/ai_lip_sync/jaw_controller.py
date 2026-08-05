"""Jaw Controller — jaw drop follows mouth openness with smoothing."""
from __future__ import annotations

from typing import Any


def jaw_curve(timeline: list[dict[str, Any]], *, smoothing: int = 2) -> list[dict[str, Any]]:
    """Return per-frame jaw-drop values (0-1), smoothed over neighbours."""
    raw = [f.get("open", 0.0) for f in timeline]
    n = len(raw)
    smoothed = [0.0] * n
    for i in range(n):
        lo = max(0, i - smoothing)
        hi = min(n, i + smoothing + 1)
        smoothed[i] = sum(raw[lo:hi]) / (hi - lo)
    return [
        {"frame": f.get("frame"), "time": f.get("time"), "value": round(v, 3)}
        for f, v in zip(timeline, smoothed, strict=False)
    ]
