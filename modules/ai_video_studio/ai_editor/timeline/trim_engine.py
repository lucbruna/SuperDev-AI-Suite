"""Trim engine — trim, roll and extend edits.

* ``trim`` — set a clip's new in/out points directly.
* ``roll`` — move one boundary while the neighbour clips stay put (durations
  of the two adjacent clips change by ``delta``).
* ``extend`` — extend a clip's out point into a gap up to ``max_gap``.
"""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.core.exceptions import ValidationError
from modules.ai_video_studio.editor_common import make_logger

logger = make_logger("editor.trim")


class TrimEngine:
    def __init__(self, timeline: Any) -> None:
        self.timeline = timeline

    def trim(self, clip_id: str, new_start: float, new_end: float) -> dict[str, Any]:
        """Set a clip's new in/out timeline points."""
        clip = self.timeline.get_clip(clip_id)
        if new_end <= new_start:
            raise ValidationError("Trim end must be after start", field="clip")
        if new_start < 0:
            raise ValidationError("Trim start cannot be negative", field="clip")
        clip["start"] = float(new_start)
        clip["end"] = float(new_end)
        logger.info("trim %s -> [%s, %s]", clip_id, new_start, new_end)
        return clip

    def roll(self, clip_id: str, delta: float) -> dict[str, Any]:
        """Roll the clip's in point, adjusting the previous clip's out point."""
        clips = sorted(self.timeline.clips, key=lambda c: c["start"])
        idx = next((i for i, c in enumerate(clips) if c.get("id") == clip_id), None)
        if idx is None:
            raise ValidationError(f"Clip '{clip_id}' not found", field="clip_id")
        clip = clips[idx]
        new_start = clip["start"] + delta
        if new_start < 0:
            raise ValidationError("Cannot roll before zero", field="clip")
        if idx > 0:
            prev = clips[idx - 1]
            if new_start <= prev["start"]:
                raise ValidationError("Roll would overlap the previous clip", field="clip")
            prev["end"] = new_start
        clip["start"] = new_start
        return clip

    def extend(self, clip_id: str, by: float, max_gap: float = 10.0) -> dict[str, Any]:
        """Extend a clip's out point, clamping to the next clip or a gap cap."""
        clip = self.timeline.get_clip(clip_id)
        next_clip = next(
            (c for c in self.timeline.clips if c.get("track") == clip.get("track") and c["start"] >= clip["end"]),
            None,
        )
        limit = (next_clip["start"] if next_clip else clip["end"] + max_gap)
        clip["end"] = min(clip["end"] + by, limit)
        return clip
