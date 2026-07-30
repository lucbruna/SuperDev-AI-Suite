from __future__ import annotations

import time
from typing import Any


class StorageMetrics:
    """Tracks storage performance metrics."""

    def __init__(self) -> None:
        self._write_count = 0
        self._read_count = 0
        self._delete_count = 0
        self._write_errors = 0
        self._read_errors = 0

    def record_write(self, error: bool = False) -> None:
        self._write_count += 1
        if error:
            self._write_errors += 1

    def record_read(self, error: bool = False) -> None:
        self._read_count += 1
        if error:
            self._read_errors += 1

    def record_delete(self) -> None:
        self._delete_count += 1

    def collect(self) -> dict[str, Any]:
        return {
            "write_count": self._write_count,
            "read_count": self._read_count,
            "delete_count": self._delete_count,
            "write_errors": self._write_errors,
            "read_errors": self._read_errors,
            "timestamp": time.time(),
        }
