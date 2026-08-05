"""Ripple edits — delete and slice with content following the edit.

A ripple edit removes a clip (or the segment after a split) and shifts every
later clip on the same track left by the removed duration, closing the gap.
"""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.core.exceptions import ValidationError
from modules.ai_video_studio.editor_common import make_logger

logger = make_logger("editor.ripple")


class RippleEdit:
    def __init__(self, timeline: Any) -> None:
        self.timeline = timeline

    def delete(self, clip_id: str) -> dict[str, Any] | None:
        """Ripple-delete a clip: close the gap on its track."""
        clip = self.timeline.get_clip(clip_id)
        gap = clip["end"] - clip["start"]
        removed = self.timeline.remove_clip(clip_id)
        self._shift_after(clip.get("track", "video"), clip["end"], -gap)
        logger.info("ripple delete %s (gap %.2fs)", clip_id, gap)
        return removed

    def slice(self, clip_id: str, at: float) -> list[dict[str, Any]]:
        """Split ``clip_id`` at timeline time ``at`` and ripple nothing yet."""
        clip = self.timeline.get_clip(clip_id)
        if not (clip["start"] < at < clip["end"]):
            raise ValidationError(f"Slice point {at} must be inside the clip", field="time")
        tail = dict(clip)
        tail["id"] = f"{clip['id']}_tail"
        tail["start"] = at
        tail["source_in"] = float(clip.get("source_in", 0)) + (at - clip["start"])
        clip["end"] = at
        self.timeline.clips.append(tail)
        logger.info("ripple slice %s at %.2f -> %s", clip_id, at, tail["id"])
        return [clip, tail]

    def _shift_after(self, track: str, after: float, delta: float) -> None:
        for clip in self.timeline.clips:
            if clip.get("track") == track and clip["start"] >= after:
                clip["start"] += delta
                clip["end"] += delta
