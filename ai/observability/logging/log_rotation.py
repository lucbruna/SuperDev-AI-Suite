"""Log rotation."""

from __future__ import annotations

import time
from typing import Any


class LogRotation:
    def __init__(self, max_size_mb: int = 100, max_files: int = 10) -> None:
        self._max_size = max_size_mb * 1024 * 1024
        self._max_files = max_files
        self._current_size = 0
        self._files: list[dict[str, Any]] = []
        self._rotations = 0

    def should_rotate(self, entry_size: int = 100) -> bool:
        return self._current_size + entry_size > self._max_size

    def rotate(self) -> dict[str, Any]:
        self._rotations += 1
        file_entry = {"file_id": f"rot_{self._rotations}", "size": self._current_size, "timestamp": time.time()}
        self._files.append(file_entry)
        if len(self._files) > self._max_files:
            self._files = self._files[-self._max_files :]
        self._current_size = 0
        return file_entry

    def add_size(self, size: int) -> None:
        self._current_size += size

    def get_status(self) -> dict[str, Any]:
        return {
            "current_size": self._current_size,
            "max_size": self._max_size,
            "files": len(self._files),
            "rotations": self._rotations,
        }

    def get_files(self) -> list[dict[str, Any]]:
        return list(self._files)
