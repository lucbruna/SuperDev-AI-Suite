"""Editor history — versioned project snapshots with restore.

Every ``commit`` stores a deep copy of the timeline keyed by a version id with
a timestamp and label, so a project can be rolled back to any point.
"""
from __future__ import annotations

import copy
import time
import uuid
from typing import Any

from modules.ai_video_studio.core.exceptions import ValidationError
from modules.ai_video_studio.editor_common import make_logger

logger = make_logger("editor.history")


class EditorHistory:
    def __init__(self, *, keep: int = 50) -> None:
        self._versions: list[dict[str, Any]] = []
        self.keep = max(1, keep)

    def commit(self, timeline: dict[str, Any], label: str = "edit") -> str:
        """Store a snapshot; returns the version id."""
        version_id = uuid.uuid4().hex[:10]
        self._versions.append({
            "id": version_id,
            "label": label,
            "timestamp": time.time(),
            "timeline": copy.deepcopy(timeline),
        })
        if len(self._versions) > self.keep:
            self._versions.pop(0)
        return version_id

    def restore(self, version_id: str) -> dict[str, Any] | None:
        for version in self._versions:
            if version["id"] == version_id:
                return copy.deepcopy(version["timeline"])
        raise ValidationError(f"Version '{version_id}' not found", field="version")

    def latest(self) -> dict[str, Any] | None:
        if not self._versions:
            return None
        return copy.deepcopy(self._versions[-1]["timeline"])

    def versions(self) -> list[dict[str, Any]]:
        return [{"id": v["id"], "label": v["label"], "timestamp": v["timestamp"]} for v in self._versions]

    def clear(self) -> None:
        self._versions.clear()
