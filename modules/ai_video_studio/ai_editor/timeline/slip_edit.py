"""Slip edit — change a clip's source in/out without moving its position.

The clip keeps its timeline start/end but reveals different media content.
Useful when the placed duration is correct but the shown frames are not.
"""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.core.exceptions import ValidationError
from modules.ai_video_studio.editor_common import make_logger

logger = make_logger("editor.slip")


class SlipEdit:
    def __init__(self, timeline: Any) -> None:
        self.timeline = timeline

    def slip(self, clip_id: str, delta: float) -> dict[str, Any]:
        """Shift the source window by ``delta`` seconds (keeps duration)."""
        clip = self.timeline.get_clip(clip_id)
        source_in = float(clip.get("source_in", 0))
        source_duration = clip["end"] - clip["start"]
        new_in = source_in + delta
        if new_in < 0:
            raise ValidationError("Cannot slip before the start of the source", field="clip")
        clip["source_in"] = new_in
        clip["source_out"] = new_in + source_duration
        logger.info("slip %s by %.2f -> source_in=%.2f", clip_id, delta, new_in)
        return clip
