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


def studio_camera_move(studio_id: str, scene_index: int, total_frames: int) -> dict[str, Any]:
    """Create a restrained, alternating move suited to the selected visual style."""
    if total_frames < 2:
        total_frames = 2
    direction = -1 if scene_index % 2 else 1
    if studio_id == "historical_documentary":
        start_zoom, end_zoom = 1.015, 1.085
        pan = 18.0 * direction
        roll = 0.18 * direction
    elif studio_id == "whymentary":
        start_zoom, end_zoom = 1.0, 1.025
        pan = 5.0 * direction
        roll = 0.0
    else:
        raise ValueError(f"Unknown studio '{studio_id}'")
    return {
        "keyframes": [
            {"frame": 0, "dx": -pan, "dy": 2.0 * direction, "zoom": start_zoom, "roll": -roll},
            {"frame": total_frames // 2, "dx": 0.0, "dy": 0.0, "zoom": (start_zoom + end_zoom) / 2, "roll": 0.0},
            {"frame": total_frames - 1, "dx": pan, "dy": -2.0 * direction, "zoom": end_zoom, "roll": roll},
        ]
    }
