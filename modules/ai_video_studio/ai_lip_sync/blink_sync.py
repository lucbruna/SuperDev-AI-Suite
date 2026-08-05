"""Blink Sync — a natural, deterministic blink schedule for the timeline."""
from __future__ import annotations

import random
from typing import Any

AVG_BLINK_INTERVAL = 3.8
BLINK_DURATION = 0.12


def blink_schedule(duration: float, *, fps: int = 24, seed: int = 42) -> list[dict[str, Any]]:
    """Return ``[{time, duration}]`` blink events (deterministic)."""
    rng = random.Random(seed)
    events: list[dict[str, Any]] = []
    t = rng.uniform(0.8, 2.0)
    while t < duration - 0.3:
        events.append({"time": round(t, 3), "duration": BLINK_DURATION})
        t += rng.uniform(1.5, 5.5)
    return events


def apply_blinks(timeline: list[dict[str, Any]], *, fps: int = 24) -> list[dict[str, Any]]:
    """Attach a per-frame ``_blink`` flag (0 = closed, 1 = open) to frames."""
    if not timeline:
        return timeline
    duration = timeline[-1]["time"]
    events = blink_schedule(duration, fps=fps)
    out: list[dict[str, Any]] = []
    for f in timeline:
        t = f.get("time", 0.0)
        blinking = any(e["time"] <= t < e["time"] + e["duration"] for e in events)
        out.append({**f, "_blink": 0.0 if blinking else 1.0})
    return out
