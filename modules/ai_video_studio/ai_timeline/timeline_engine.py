"""Timeline engine — core multi-track timeline orchestration.

Manages clips on the timeline: adding/removing, overlap validation, total
duration and ordering. This is the "AI Timeline" (blueprint Volume 2) core.
"""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.core.exceptions import ValidationError


class TimelineEngine:
    """Orchestrates a video timeline: clips, duration and validation."""

    def __init__(self) -> None:
        self.clips: list[dict[str, Any]] = []
        self.tracks: dict[str, list[dict[str, Any]]] = {}

    def add_clip(self, clip: dict[str, Any], track: str = "video") -> dict[str, Any]:
        """Add a clip to the timeline after validating placement.

        Clips must have ``start`` and ``end`` (seconds) and must not overlap
        existing clips on the same track.
        """
        self._validate_clip(clip)
        errors = self.validate_placement(clip, track=track)
        if errors:
            raise ValidationError("; ".join(errors), field="clip")
        clip.setdefault("id", clip.get("id") or f"clip_{len(self.clips) + 1}")
        clip.setdefault("track", track)
        self.clips.append(clip)
        self.tracks.setdefault(track, []).append(clip)
        self._sort(track)
        return clip

    def _validate_clip(self, clip: dict[str, Any]) -> None:
        start = clip.get("start")
        end = clip.get("end")
        if not isinstance(start, (int, float)) or not isinstance(end, (int, float)):
            raise ValidationError("Clip must have numeric start and end", field="clip")
        if end <= start:
            raise ValidationError("Clip end must be after start", field="clip")
        if start < 0:
            raise ValidationError("Clip start cannot be negative", field="clip")

    def validate_placement(self, clip: dict[str, Any], track: str = "video") -> list[str]:
        """Return a list of placement errors (empty when valid)."""
        errors: list[str] = []
        new_start = clip.get("start", 0)
        new_end = clip.get("end", 0)
        if new_end <= new_start:
            errors.append("Clip end must be after start")
        for existing in self.tracks.get(track, []):
            if existing.get("id") == clip.get("id"):
                continue
            if new_start < existing["end"] and new_end > existing["start"]:
                errors.append(f"Overlaps with clip on track '{track}'")
        return errors

    def remove_clip(self, clip_id: str) -> dict[str, Any] | None:
        """Remove a clip by id from all tracks."""
        removed = None
        self.clips = [c for c in self.clips if c.get("id") != clip_id]
        for track, clips in list(self.tracks.items()):
            before = len(clips)
            self.tracks[track] = [c for c in clips if c.get("id") != clip_id]
            if len(self.tracks[track]) != before:
                removed = next((c for c in clips if c.get("id") == clip_id), None)
        return removed

    def move_clip(self, clip_id: str, start: float, track: str | None = None) -> dict[str, Any]:
        """Move a clip to a new start position (and optionally a track)."""
        for clip in self.clips:
            if clip.get("id") == clip_id:
                old_start, old_end = clip["start"], clip["end"]
                duration = old_end - old_start
                candidate = {**clip, "start": start, "end": start + duration}
                if track is not None:
                    candidate["track"] = track
                errors = self.validate_placement(candidate, track=candidate["track"])
                if errors:
                    raise ValidationError("; ".join(errors), field="clip")
                if track is not None:
                    self.remove_clip(clip_id)
                    clip.update(candidate)
                    self.add_clip(clip)
                else:
                    clip["start"] = start
                    clip["end"] = start + duration
                    self._sort(clip["track"])
                return clip
        raise ValidationError(f"Clip '{clip_id}' not found", field="clip_id")

    def trim_clip(self, clip_id: str, new_start: float, new_end: float) -> dict[str, Any]:
        """Trim a clip to new in/out points."""
        for clip in self.clips:
            if clip.get("id") == clip_id:
                if new_end <= new_start:
                    raise ValidationError("Trim end must be after start", field="clip")
                clip["start"] = new_start
                clip["end"] = new_end
                return clip
        raise ValidationError(f"Clip '{clip_id}' not found", field="clip_id")

    def duration(self) -> float:
        """Total timeline duration = max end across all clips."""
        if not self.clips:
            return 0.0
        return max(c["end"] for c in self.clips)

    def clip_count(self) -> int:
        return len(self.clips)

    def track_names(self) -> list[str]:
        return list(self.tracks.keys())

    def clips_on(self, track: str) -> list[dict[str, Any]]:
        return list(self.tracks.get(track, []))

    def ordered_clips(self) -> list[dict[str, Any]]:
        return sorted(self.clips, key=lambda c: (c["start"], c.get("track", "")))

    def to_dict(self) -> dict[str, Any]:
        return {
            "duration": self.duration(),
            "clip_count": self.clip_count(),
            "tracks": {name: list(clips) for name, clips in self.tracks.items()},
        }

    def _sort(self, track: str) -> None:
        self.tracks[track] = sorted(self.tracks[track], key=lambda c: c["start"])


_timeline_engine: TimelineEngine | None = None


def get_timeline_engine() -> TimelineEngine:
    """Cached singleton timeline engine."""
    global _timeline_engine
    if _timeline_engine is None:
        _timeline_engine = TimelineEngine()
    return _timeline_engine
