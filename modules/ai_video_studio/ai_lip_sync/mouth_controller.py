"""Mouth Controller — per-frame mouth parameter curves from the viseme timeline."""
from __future__ import annotations

from typing import Any


def mouth_curves(timeline: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Extract mouth params (open/round/wide/tense) per frame."""
    return [
        {
            "frame": f.get("frame"),
            "time": f.get("time"),
            "open": f.get("open", 0.0),
            "round": f.get("round", 0.0),
            "wide": f.get("wide", 0.0),
            "tense": f.get("tense", 0.0),
            "viseme": f.get("viseme", "neutral"),
        }
        for f in timeline
    ]


def mouth_open_curve(timeline: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Just the jaw-open curve (useful for blendshape drivers)."""
    return [{"frame": f.get("frame"), "time": f.get("time"),
             "value": f.get("open", 0.0)} for f in timeline]
