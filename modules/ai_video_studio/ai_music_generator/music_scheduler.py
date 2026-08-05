"""Music Scheduler — orders track rendering and reports progress."""
from __future__ import annotations

import logging
from typing import Any, Callable

logger = logging.getLogger(__name__)


class MusicScheduler:
    """Runs track rendering with an optional progress callback."""

    def __init__(self) -> None:
        self._progress: Callable[[dict[str, Any]], None] | None = None

    def on_progress(self, callback: Callable[[dict[str, Any]], None]) -> None:
        self._progress = callback

    def report(self, *, done: int, total: int, track: str) -> None:
        if self._progress is not None:
            try:
                self._progress({"done": done, "total": total, "track": track})
            except Exception as e:  # noqa: BLE001
                logger.debug("progress callback failed: %s", e)

    def schedule(self, track_names: list[str]) -> list[str]:
        # Keep the defined order; rendering is CPU-bound and sequential.
        return list(track_names)
