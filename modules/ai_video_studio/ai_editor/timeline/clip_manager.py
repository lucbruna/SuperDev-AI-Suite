"""Clip manager — clip CRUD and property editing.

Extends the timeline with typed helpers for setting speed, opacity, source
windows and transforms, and queries for finding clips on the playhead.
"""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.core.exceptions import ValidationError
from modules.ai_video_studio.editor_common import make_logger

logger = make_logger("editor.clips")


class ClipManager:
    def __init__(self, timeline: Any) -> None:
        self.timeline = timeline

    def add(self, clip: dict[str, Any], track: str = "video") -> dict[str, Any]:
        return self.timeline.add_clip(clip, track=track)

    def get(self, clip_id: str) -> dict[str, Any]:
        return self.timeline.get_clip(clip_id)

    def remove(self, clip_id: str) -> dict[str, Any] | None:
        return self.timeline.remove_clip(clip_id)

    def set_speed(self, clip_id: str, speed: float) -> dict[str, Any]:
        if speed <= 0:
            raise ValidationError("Speed must be positive", field="speed")
        clip = self.timeline.get_clip(clip_id)
        clip["speed"] = float(speed)
        return clip

    def set_opacity(self, clip_id: str, opacity: float) -> dict[str, Any]:
        clip = self.timeline.get_clip(clip_id)
        clip["opacity"] = max(0.0, min(1.0, opacity))
        return clip

    def set_transform(self, clip_id: str, **transform: Any) -> dict[str, Any]:
        clip = self.timeline.get_clip(clip_id)
        clip.setdefault("transform", {})
        for key, value in transform.items():
            if key not in {"x", "y", "scale", "rotation"}:
                raise ValidationError(f"Unknown transform '{key}'", field="transform")
            clip["transform"][key] = value
        return clip

    def set_source_window(self, clip_id: str, source_in: float, source_out: float) -> dict[str, Any]:
        if source_out <= source_in:
            raise ValidationError("source_out must be after source_in", field="source")
        clip = self.timeline.get_clip(clip_id)
        clip["source_in"] = float(source_in)
        clip["source_out"] = float(source_out)
        return clip

    def clips_under_playhead(self, time: float) -> list[dict[str, Any]]:
        return self.timeline.clips_at(time)

    def clips_in_range(self, start: float, end: float) -> list[dict[str, Any]]:
        return [
            c for c in self.timeline.clips
            if c["end"] > start and c["start"] < end
        ]
