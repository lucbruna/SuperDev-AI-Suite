"""Eased camera keyframes and studio-aware cinematic move presets."""
from __future__ import annotations

from typing import Any


_CAMERA_FIELDS = ("dx", "dy", "zoom", "roll")


def camera_state_at_frame(camera: dict[str, Any], frame_index: int) -> dict[str, float]:
    """Interpolate camera keyframes with smoothstep easing between key poses."""
    keyframes = camera.get("keyframes")
    if not isinstance(keyframes, list) or len(keyframes) < 2:
        raise ValueError("camera keyframes must contain at least two entries")
    frames: list[tuple[int, dict[str, float]]] = []
    for item in keyframes:
        if not isinstance(item, dict) or "frame" not in item:
            raise ValueError("each camera keyframe requires a frame number")
        frame = int(item["frame"])
        values = {field: float(item.get(field, {"dx": 0, "dy": 0, "zoom": 1, "roll": 0}[field])) for field in _CAMERA_FIELDS}
        if values["zoom"] <= 0:
            raise ValueError("camera zoom must be greater than zero")
        frames.append((frame, values))
    if any(right[0] <= left[0] for left, right in zip(frames, frames[1:])):
        raise ValueError("camera keyframe positions must be strictly increasing")
    if frame_index <= frames[0][0]:
        return frames[0][1]
    if frame_index >= frames[-1][0]:
        return frames[-1][1]
    for (start, a), (end, b) in zip(frames, frames[1:]):
        if start <= frame_index <= end:
            t = (frame_index - start) / (end - start)
            eased = t * t * (3.0 - 2.0 * t)
            return {field: a[field] + (b[field] - a[field]) * eased for field in _CAMERA_FIELDS}
    return frames[-1][1]


def studio_camera_move(
    studio_id: str, scene_index: int, total_frames: int, shot_type: str = "medium"
) -> dict[str, Any]:
    """Create a shot-aware camera move, alternating direction between scenes."""
    if total_frames < 2:
        total_frames = 2
    direction = -1 if scene_index % 2 else 1
    if studio_id == "historical_documentary":
        ranges = {
            "establishing": (1.005, 1.045, 24.0, 0.08),
            "wide": (1.0, 1.03, 12.0, 0.0),
            "medium": (1.015, 1.075, 18.0, 0.12),
            "close_up": (1.035, 1.12, 8.0, 0.08),
            "detail": (1.06, 1.15, 5.0, 0.04),
            "tracking": (1.01, 1.065, 34.0, 0.1),
        }
    elif studio_id == "whymentary":
        ranges = {
            "establishing": (1.0, 1.015, 7.0, 0.0),
            "wide": (1.0, 1.01, 3.0, 0.0),
            "medium": (1.0, 1.02, 5.0, 0.0),
            "close_up": (1.005, 1.03, 2.0, 0.0),
            "detail": (1.01, 1.035, 1.0, 0.0),
            "tracking": (1.0, 1.02, 9.0, 0.0),
        }
    elif studio_id == "felt_clay":
        ranges = {
            "establishing": (1.0, 1.025, 8.0, 0.0),
            "wide": (1.0, 1.02, 5.0, 0.0),
            "medium": (1.005, 1.035, 7.0, 0.0),
            "close_up": (1.015, 1.055, 3.0, 0.0),
            "detail": (1.02, 1.065, 2.0, 0.0),
            "tracking": (1.0, 1.03, 10.0, 0.0),
        }
    else:
        # Neutral cinematic movement for custom user-defined art direction.
        ranges = {
            "establishing": (1.0, 1.035, 18.0, 0.0),
            "wide": (1.0, 1.025, 12.0, 0.0),
            "medium": (1.005, 1.05, 14.0, 0.0),
            "close_up": (1.02, 1.075, 6.0, 0.0),
            "detail": (1.03, 1.085, 4.0, 0.0),
            "tracking": (1.0, 1.045, 24.0, 0.0),
        }
    if shot_type not in ranges:
        raise ValueError(f"Unknown shot type '{shot_type}'")
    start_zoom, end_zoom, pan, roll = ranges[shot_type]
    pan *= direction
    roll *= direction
    return {
        "keyframes": [
            {"frame": 0, "dx": -pan, "dy": 2.0 * direction, "zoom": start_zoom, "roll": -roll},
            {"frame": total_frames // 2, "dx": 0.0, "dy": 0.0, "zoom": (start_zoom + end_zoom) / 2, "roll": 0.0},
            {"frame": total_frames - 1, "dx": pan, "dy": -2.0 * direction, "zoom": end_zoom, "roll": roll},
        ]
    }
