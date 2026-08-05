"""Clip manager — add, move, trim, split and duplicate clips."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.core.exceptions import ValidationError


class ClipManager:
    """High-level clip operations layered on top of a timeline engine."""

    def __init__(self, engine: Any | None = None) -> None:
        if engine is None:
            from modules.ai_video_studio.ai_timeline.timeline_engine import get_timeline_engine

            engine = get_timeline_engine()
        self.engine = engine

    def add(self, clip: dict[str, Any], track: str = "video") -> dict[str, Any]:
        return self.engine.add_clip(clip, track=track)

    def move(self, clip_id: str, start: float, track: str | None = None) -> dict[str, Any]:
        return self.engine.move_clip(clip_id, start, track=track)

    def trim(self, clip_id: str, new_start: float, new_end: float) -> dict[str, Any]:
        return self.engine.trim_clip(clip_id, new_start, new_end)

    def split(self, clip_id: str, at: float) -> list[dict[str, Any]]:
        """Split a clip into two at a given time offset."""
        clip = self._find(clip_id)
        if at <= clip["start"] or at >= clip["end"]:
            raise ValidationError("Split point must be inside the clip", field="at")
        left = {**clip, "id": f"{clip_id}_a", "end": at}
        right = {**clip, "id": f"{clip_id}_b", "start": at}
        self.engine.remove_clip(clip_id)
        self.engine.add_clip(left, track=clip.get("track", "video"))
        self.engine.add_clip(right, track=clip.get("track", "video"))
        return [left, right]

    def duplicate(self, clip_id: str, offset: float = 0.0) -> dict[str, Any]:
        """Duplicate a clip, optionally offset in time."""
        clip = self._find(clip_id)
        duration = clip["end"] - clip["start"]
        copy = {
            **clip,
            "id": f"{clip_id}_copy",
            "start": clip["end"] + offset,
            "end": clip["end"] + offset + duration,
        }
        self.engine.add_clip(copy, track=clip.get("track", "video"))
        return copy

    def delete(self, clip_id: str) -> dict[str, Any] | None:
        return self.engine.remove_clip(clip_id)

    def list(self, track: str | None = None) -> list[dict[str, Any]]:
        if track is not None:
            return self.engine.clips_on(track)
        return self.engine.ordered_clips()

    def _find(self, clip_id: str) -> dict[str, Any]:
        for clip in self.engine.clips:
            if clip.get("id") == clip_id:
                return clip
        raise ValidationError(f"Clip '{clip_id}' not found", field="clip_id")


_clip_manager: ClipManager | None = None


def get_clip_manager() -> ClipManager:
    global _clip_manager
    if _clip_manager is None:
        _clip_manager = ClipManager()
    return _clip_manager
