"""Slide edit — move a clip while preserving its gap size.

When a clip slides by ``delta``, the neighbouring clip's boundary moves with
it so the gap between them stays constant (the source window is preserved).
"""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.core.exceptions import ValidationError
from modules.ai_video_studio.editor_common import make_logger

logger = make_logger("editor.slide")


class SlideEdit:
    def __init__(self, timeline: Any) -> None:
        self.timeline = timeline

    def slide(self, clip_id: str, delta: float) -> dict[str, Any]:
        """Slide the clip by ``delta`` while preserving the gap to neighbours."""
        clip = self.timeline.get_clip(clip_id)
        track_clips = sorted(
            (c for c in self.timeline.clips if c.get("track") == clip.get("track")),
            key=lambda c: c["start"],
        )
        idx = next((i for i, c in enumerate(track_clips) if c.get("id") == clip_id), None)
        if idx is None:
            raise ValidationError(f"Clip '{clip_id}' not found", field="clip_id")
        duration = clip["end"] - clip["start"]
        new_start = clip["start"] + delta
        if new_start < 0:
            raise ValidationError("Cannot slide before zero", field="clip")
        # Keep the same gap to the previous clip by moving its out point.
        if idx > 0:
            prev = track_clips[idx - 1]
            if new_start <= prev["start"]:
                raise ValidationError("Slide would overlap the previous clip", field="clip")
            prev["end"] = new_start
        clip["start"] = new_start
        clip["end"] = new_start + duration
        logger.info("slide %s by %.2f -> [%.2f, %.2f]", clip_id, delta, new_start, new_start + duration)
        return clip
