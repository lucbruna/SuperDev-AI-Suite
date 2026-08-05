"""Track manager — manage video, audio, subtitle and effect tracks."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.core.exceptions import ValidationError

VALID_TRACK_TYPES = ("video", "audio", "subtitle", "effect", "transition")


class TrackManager:
    """Creates and manages named tracks on a timeline."""

    def __init__(self, engine: Any | None = None) -> None:
        if engine is None:
            from modules.ai_video_studio.ai_timeline.timeline_engine import get_timeline_engine

            engine = get_timeline_engine()
        self.engine = engine
        self._metadata: dict[str, dict[str, Any]] = {}

    def create_track(self, name: str, track_type: str = "video", **meta: Any) -> dict[str, Any]:
        if track_type not in VALID_TRACK_TYPES:
            raise ValidationError(
                f"Invalid track type '{track_type}'. Use: {', '.join(VALID_TRACK_TYPES)}",
                field="track_type",
            )
        if name in self._metadata:
            raise ValidationError(f"Track '{name}' already exists", field="name")
        self.engine.tracks.setdefault(name, [])
        self._metadata[name] = {"name": name, "type": track_type, "muted": False, "locked": False, **meta}
        return self._metadata[name]

    def get(self, name: str) -> dict[str, Any] | None:
        return self._metadata.get(name)

    def list(self) -> list[dict[str, Any]]:
        return [self._metadata[n] for n in self.engine.track_names() if n in self._metadata]

    def delete(self, name: str) -> bool:
        if name not in self._metadata:
            return False
        del self._metadata[name]
        self.engine.tracks.pop(name, None)
        return True

    def set_muted(self, name: str, muted: bool) -> dict[str, Any]:
        meta = self._require(name)
        meta["muted"] = muted
        return meta

    def set_locked(self, name: str, locked: bool) -> dict[str, Any]:
        meta = self._require(name)
        meta["locked"] = locked
        return meta

    def _require(self, name: str) -> dict[str, Any]:
        meta = self._metadata.get(name)
        if meta is None:
            raise ValidationError(f"Track '{name}' not found", field="name")
        return meta


_track_manager: TrackManager | None = None


def get_track_manager() -> TrackManager:
    global _track_manager
    if _track_manager is None:
        _track_manager = TrackManager()
    return _track_manager
