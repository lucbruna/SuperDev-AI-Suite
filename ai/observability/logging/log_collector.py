"""Log collector."""
from __future__ import annotations

import time
import uuid
from typing import Any


class LogCollector:
    def __init__(self, buffer_size: int = 1000) -> None:
        self._buffer: list[dict[str, Any]] = []
        self._buffer_size = buffer_size
        self._flushed = 0
    def collect(self, entry: dict[str, Any]) -> bool:
        entry.setdefault("id", str(uuid.uuid4())[:8])
        entry.setdefault("timestamp", time.time())
        self._buffer.append(entry)
        if len(self._buffer) >= self._buffer_size:
            self.flush()
        return True
    def flush(self) -> int:
        n = len(self._buffer)
        self._buffer = []
        self._flushed += n
        return n
    def get_buffer(self) -> list[dict[str, Any]]:
        return list(self._buffer)
    def buffer_size(self) -> int:
        return len(self._buffer)
    def total_flushed(self) -> int:
        return self._flushed
