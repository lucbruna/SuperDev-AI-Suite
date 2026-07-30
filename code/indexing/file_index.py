from __future__ import annotations

import logging
from typing import Any


class FileIndex:
    """Indexes files by path and metadata."""

    def __init__(self) -> None:
        self._files: dict[str, dict[str, Any]] = {}
        self._log = logging.getLogger("superdev.code.indexing.files")

    def add(self, path: str, metadata: dict[str, Any]) -> None:
        self._files[path] = metadata

    def get(self, path: str) -> dict[str, Any] | None:
        return self._files.get(path)
