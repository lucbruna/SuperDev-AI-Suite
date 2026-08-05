"""Nested sequences — group clips into a single nested-sequence clip.

Nesting replaces a range of clips on a track with one "nested" clip whose
``sequence`` field holds the sub-timeline. Flattening expands it back.
Nested clips can be nested again, enabling multi-level composition.
"""
from __future__ import annotations

import uuid
from typing import Any

from modules.ai_video_studio.core.exceptions import ValidationError
from modules.ai_video_studio.editor_common import make_logger

logger = make_logger("editor.nesting")


class NestedSequences:
    def __init__(self, timeline: Any) -> None:
        self.timeline = timeline

    def nest(self, clip_ids: list[str], track: str | None = None) -> dict[str, Any]:
        """Replace ``clip_ids`` with a nested-sequence clip covering their range."""
        if not clip_ids:
            raise ValidationError("No clips to nest", field="clips")
        clips = [self.timeline.get_clip(cid) for cid in clip_ids]
        if track is None:
            track = clips[0].get("track", "video")
        for clip in clips[1:]:
            if clip.get("track") != track:
                raise ValidationError("Can only nest clips on the same track", field="clips")
        start = min(c["start"] for c in clips)
        end = max(c["end"] for c in clips)
        for clip in clips:
            self.timeline.remove_clip(clip["id"])
        nested: dict[str, Any] = {
            "id": f"nested_{uuid.uuid4().hex[:8]}",
            "track": track,
            "start": start,
            "end": end,
            "nested": True,
            "sequence": {
                "fps": self.timeline.fps,
                "clips": [dict(c) for c in clips],
            },
        }
        self.timeline.add_clip(nested, track=track)
        logger.info("nested %d clips -> %s [%.2f, %.2f]", len(clips), nested["id"], start, end)
        return nested

    def flatten(self, clip_id: str) -> list[dict[str, Any]]:
        """Expand a nested clip back into its child clips."""
        clip = self.timeline.get_clip(clip_id)
        sequence = clip.get("sequence")
        if not sequence:
            raise ValidationError(f"Clip '{clip_id}' is not nested", field="clip_id")
        track = clip.get("track", "video")
        offset = clip["start"]
        self.timeline.remove_clip(clip_id)
        restored: list[dict[str, Any]] = []
        for child in sequence.get("clips", []):
            child = dict(child)
            child["start"] = float(child["start"]) + offset
            child["end"] = float(child["end"]) + offset
            child["track"] = track
            restored.append(self.timeline.add_clip(child, track=track))
        return restored
