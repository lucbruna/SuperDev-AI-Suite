"""Multi-track manager — track lifecycle and per-track state.

Owns track creation/removal/order plus per-track flags (muted, locked,
hidden). A locked track rejects clip edits; muted audio tracks are skipped
during render.
"""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.core.exceptions import ValidationError
from modules.ai_video_studio.editor_common import make_logger

logger = make_logger("editor.tracks")


class MultiTrackManager:
    def __init__(self, timeline: Any) -> None:
        self.timeline = timeline

    def add(self, name: str, track_type: str = "video") -> dict[str, Any]:
        return self.timeline.add_track(name, track_type)

    def remove(self, name: str) -> bool:
        return self.timeline.remove_track(name)

    def ensure(self, name: str, track_type: str = "video") -> dict[str, Any]:
        return self.timeline.ensure_track(name, track_type)

    def set_flag(self, name: str, flag: str, value: bool) -> dict[str, Any]:
        return self.timeline.set_track_flag(name, flag, value)

    def assert_unlocked(self, name: str) -> None:
        track = self.timeline.tracks.get(name)
        if track and track.get("locked"):
            raise ValidationError(f"Track '{name}' is locked", field="track")

    def visible_tracks(self, track_type: str) -> list[str]:
        return [
            name for name, t in self.timeline.tracks.items()
            if t.get("type") == track_type and not t.get("hidden")
        ]

    def audible_tracks(self) -> list[str]:
        return [
            name for name, t in self.timeline.tracks.items()
            if t.get("type") == "audio" and not t.get("muted")
        ]

    def order(self) -> list[str]:
        return list(self.timeline.tracks.keys())

    def move_track(self, name: str, index: int) -> list[str]:
        if name not in self.timeline.tracks:
            raise ValidationError(f"Track '{name}' not found", field="track")
        ordered = self.order()
        ordered.remove(name)
        ordered.insert(max(0, min(index, len(ordered))), name)
        # Rebuild the dict preserving the new order.
        reordered: dict[str, Any] = {}
        for key in ordered:
            reordered[key] = self.timeline.tracks[key]
        self.timeline.tracks = reordered
        return ordered
