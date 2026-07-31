"""Wiki version history."""

from __future__ import annotations

import time
from typing import Any


class VersionEntry:
    """One snapshot of a wiki page."""

    def __init__(self, document_id: str, version: int, title: str,
                 body: str, editor_id: str) -> None:
        self.document_id = document_id
        self.version = version
        self.title = title
        self.body = body
        self.editor_id = editor_id
        self.timestamp = time.time()

    def to_dict(self) -> dict[str, Any]:
        return {"document_id": self.document_id, "version": self.version,
                "title": self.title, "body": self.body,
                "editor_id": self.editor_id, "timestamp": self.timestamp}


class VersionHistory:
    """Tracks every version of a page (max 50)."""

    def __init__(self, max_versions: int = 50) -> None:
        self.max_versions = max_versions
        self._versions: list[VersionEntry] = []

    def snapshot(self, document_id: str, version: int, title: str,
                 body: str, editor_id: str) -> None:
        self._versions.append(VersionEntry(document_id, version, title,
                                           body, editor_id))
        if len(self._versions) > self.max_versions:
            self._versions = self._versions[-self.max_versions:]

    def list(self) -> list[VersionEntry]:
        return list(self._versions)

    def get(self, version: int) -> VersionEntry | None:
        for entry in self._versions:
            if entry.version == version:
                return entry
        return None

    def latest(self) -> VersionEntry | None:
        return self._versions[-1] if self._versions else None

    def count(self) -> int:
        return len(self._versions)
