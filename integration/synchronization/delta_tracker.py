"""Delta tracking for incremental synchronization."""

from __future__ import annotations

import time
from typing import Any


class DeltaTracker:
    """Tracks the last synchronized watermark per source entity."""

    def __init__(self) -> None:
        self._watermarks: dict[str, Any] = {}
        self._updated: dict[str, float] = {}

    def set_watermark(self, source: str, value: Any) -> None:
        self._watermarks[source] = value
        self._updated[source] = time.time()

    def watermark(self, source: str) -> Any:
        return self._watermarks.get(source)

    def has_changes_since(self, source: str, value: Any) -> bool:
        """True when `value` is newer than the recorded watermark."""
        current = self.watermark(source)
        if current is None:
            return True
        try:
            return value > current
        except TypeError:
            return value != current

    def sources(self) -> list[str]:
        return sorted(self._watermarks)
