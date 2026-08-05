"""Clipboard manager — copy/cut/paste of clips across the timeline.

Clipboard holds deep copies of clips with new ids; pasting places them at a
given time, preserving their relative offsets so multi-clip selections paste
as a block.
"""
from __future__ import annotations

import copy
import uuid
from typing import Any

from modules.ai_video_studio.editor_common import make_logger

logger = make_logger("editor.clipboard")


class ClipboardManager:
    def __init__(self) -> None:
        self._clips: list[dict[str, Any]] = []
        self._cut: list[dict[str, Any]] = []

    def copy_clip(self, clip: dict[str, Any]) -> int:
        """Copy a clip (deep copy, fresh id). Returns clipboard size."""
        item = copy.deepcopy(clip)
        item["id"] = f"clip_{uuid.uuid4().hex[:8]}"
        self._clips.append(item)
        return len(self._clips)

    def cut_clip(self, clip: dict[str, Any]) -> int:
        """Cut: copy for paste and remember the original for deletion."""
        self.copy_clip(clip)
        self._cut.append(clip.get("id"))
        return len(self._cut)

    def paste_clip(self, time: float) -> dict[str, Any]:
        """Return the last copied clip placed at ``time`` (new id again)."""
        if not self._clips:
            raise ValueError("Clipboard is empty")
        clip = copy.deepcopy(self._clips[-1])
        clip["id"] = f"clip_{uuid.uuid4().hex[:8]}"
        duration = clip["end"] - clip["start"]
        clip["start"] = time
        clip["end"] = time + duration
        return clip

    def paste_block(self, time: float) -> list[dict[str, Any]]:
        """Paste the whole selection as a block (relative offsets preserved)."""
        if not self._clips:
            return []
        base = min(c["start"] for c in self._clips)
        pasted: list[dict[str, Any]] = []
        for clip in sorted(self._clips, key=lambda c: c["start"]):
            item = copy.deepcopy(clip)
            item["id"] = f"clip_{uuid.uuid4().hex[:8]}"
            duration = item["end"] - item["start"]
            offset = item["start"] - base
            item["start"] = time + offset
            item["end"] = time + offset + duration
            pasted.append(item)
        return pasted

    def clear(self) -> None:
        self._clips.clear()
        self._cut.clear()

    @property
    def is_empty(self) -> bool:
        return not self._clips

    def pending_cuts(self) -> list[str]:
        return list(self._cut)
