"""Face animation — animate faces detected in an image."""
from __future__ import annotations

from typing import Any


class FaceAnimation:
    """Plans subtle facial motion (blink, micro-movement) for portraits."""

    def plan(self, faces: int = 1, *, duration: float = 4.0, fps: int = 24) -> dict[str, Any]:
        total = int(duration * fps)
        events = []
        for face in range(faces):
            blink_frame = int(total * 0.6)
            events.append({"face": face, "blink_frame": blink_frame, "micro_motion": True})
        return {"faces": faces, "events": events, "total_frames": total}

    def is_blink_frame(self, plan: dict[str, Any], face: int, frame_index: int) -> bool:
        return any(
            event["face"] == face and frame_index == event["blink_frame"]
            for event in plan.get("events", [])
        )
