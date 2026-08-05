"""Timing Optimizer — fits the dubbed soundtrack to the video duration."""
from __future__ import annotations

from typing import Any

MAX_SPEEDUP = 1.5   # stretch cap to preserve intelligibility
MAX_SLOWDOWN = 0.6


def fit_to_duration(layout: list[dict[str, Any]], video_duration: float) -> list[dict[str, Any]]:
    """Scale line timings so the whole dub fits inside ``video_duration``."""
    if not layout:
        return layout
    total = layout[-1]["end"] + layout[-1].get("pause_after", 0.0)
    if total <= video_duration:
        return layout
    factor = video_duration / total
    factor = max(MAX_SLOWDOWN, min(1.0, factor))
    out: list[dict[str, Any]] = []
    cursor = 0.0
    for line in layout:
        duration = (line["end"] - line["start"]) * factor
        entry = dict(line)
        entry["start"] = cursor
        entry["end"] = cursor + duration
        entry["duration"] = duration
        entry["speed_factor"] = factor
        out.append(entry)
        cursor = entry["end"] + line.get("pause_after", 0.0) * factor
    return out
