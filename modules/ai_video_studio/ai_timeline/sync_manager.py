"""Sync manager — audio/video/subtitle synchronization on the timeline."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.core.exceptions import ValidationError


class SyncManager:
    """Keeps related tracks aligned: audio, video, subtitles and narration."""

    def __init__(self, engine: Any | None = None) -> None:
        if engine is None:
            from modules.ai_video_studio.ai_timeline.timeline_engine import get_timeline_engine

            engine = get_timeline_engine()
        self.engine = engine
        self._groups: dict[str, list[str]] = {}

    def create_group(self, group_id: str, clip_ids: list[str]) -> dict[str, Any]:
        """Group clips that must stay in sync (move/trim together)."""
        for cid in clip_ids:
            if not any(c.get("id") == cid for c in self.engine.clips):
                raise ValidationError(f"Clip '{cid}' not found", field="clip_ids")
        self._groups[group_id] = list(clip_ids)
        return {"id": group_id, "clip_ids": self._groups[group_id]}

    def move_group(self, group_id: str, delta: float) -> list[dict[str, Any]]:
        """Shift every clip in a group by a delta (seconds)."""
        moved: list[dict[str, Any]] = []
        for cid in self._groups.get(group_id, []):
            for clip in self.engine.clips:
                if clip.get("id") == cid:
                    clip["start"] += delta
                    clip["end"] += delta
                    moved.append(clip)
                    break
        return moved

    def align_to_audio(self, group_id: str, audio_start: float) -> list[dict[str, Any]]:
        """Align all clips in a group so the first starts at audio_start."""
        clip_ids = self._groups.get(group_id, [])
        if not clip_ids:
            return []
        first = min(
            (c for c in self.engine.clips if c.get("id") in clip_ids),
            key=lambda c: c["start"],
        )
        delta = audio_start - first["start"]
        return self.move_group(group_id, delta)

    def offset(self, clip_id: str, delta: float) -> dict[str, Any]:
        """Offset a single clip (ungrouped operation)."""
        for clip in self.engine.clips:
            if clip.get("id") == clip_id:
                clip["start"] += delta
                clip["end"] += delta
                return clip
        raise ValidationError(f"Clip '{clip_id}' not found", field="clip_id")

    def is_synced(self, group_id: str) -> bool:
        """Return True when all group members share the same duration."""
        clip_ids = self._groups.get(group_id, [])
        durations: set[float] = set()
        for cid in clip_ids:
            for clip in self.engine.clips:
                if clip.get("id") == cid:
                    durations.add(round(clip["end"] - clip["start"], 3))
                    break
        return len(durations) <= 1

    def groups(self) -> dict[str, list[str]]:
        return dict(self._groups)


_sync_manager: SyncManager | None = None


def get_sync_manager() -> SyncManager:
    global _sync_manager
    if _sync_manager is None:
        _sync_manager = SyncManager()
    return _sync_manager
