"""Magnetic timeline — moving or inserting a clip pushes neighbours.

In magnetic mode, inserting a clip at a position shoves every following clip
on the same track to the right by the inserted duration, and moving a clip
before another pushes that clip right instead of overlapping it.
"""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.core.exceptions import ValidationError
from modules.ai_video_studio.editor_common import make_logger

logger = make_logger("editor.magnetic")


class MagneticTimeline:
    def __init__(self, timeline: Any) -> None:
        self.timeline = timeline

    def insert(self, clip: dict[str, Any], track: str = "video") -> dict[str, Any]:
        """Insert a clip at its start time, pushing later clips right."""
        start = clip.get("start", 0.0)
        duration = clip.get("end", start) - start
        for existing in self.timeline.clips:
            if existing.get("track") == track and existing["start"] >= start:
                existing["start"] += duration
                existing["end"] += duration
        result = self.timeline.add_clip(clip, track=track)
        logger.info("magnetic insert %s at %.2f (pushes %.2fs)", result.get("id"), start, duration)
        return result

    def move_with_magnet(self, clip_id: str, new_start: float) -> dict[str, Any]:
        """Move a clip, pushing any clip it would land on instead of overlapping."""
        clip = self.timeline.get_clip(clip_id)
        duration = clip["end"] - clip["start"]
        for other in self.timeline.clips:
            if other.get("id") == clip_id or other.get("track") != clip.get("track"):
                continue
            if new_start < other["end"] and new_start + duration > other["start"]:
                overlap = (new_start + duration) - other["start"]
                other["start"] += overlap
                other["end"] += overlap
        clip["start"] = new_start
        clip["end"] = new_start + duration
        return clip

    def push_apart(self, clip_id: str) -> list[dict[str, Any]]:
        """Resolve overlaps around ``clip_id`` by pushing overlapping clips right."""
        clip = self.timeline.get_clip(clip_id)
        touched: list[dict[str, Any]] = []
        for other in sorted(
            (c for c in self.timeline.clips if c.get("id") != clip_id and c.get("track") == clip.get("track")),
            key=lambda c: c["start"],
        ):
            if other["start"] < clip["end"]:
                overlap = clip["end"] - other["start"]
                other["start"] += overlap
                other["end"] += overlap
                touched.append(other)
        return touched
