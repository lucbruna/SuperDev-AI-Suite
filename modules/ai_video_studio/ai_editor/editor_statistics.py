"""Editor statistics — incremental per-metric tracking and reporting."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.editor_common import StatTracker, make_logger

logger = make_logger("editor.stats")


class EditorStatistics:
    """Tracks edit/render metrics with the shared StatTracker."""

    METRICS = ("edits", "renders", "previews", "undoes", "redos", "render_seconds")

    def __init__(self) -> None:
        self._trackers: dict[str, StatTracker] = {m: StatTracker() for m in self.METRICS}

    def record(self, metric: str, value: float = 1.0) -> None:
        if metric not in self._trackers:
            raise KeyError(f"Unknown metric '{metric}' (expected one of {self.METRICS})")
        self._trackers[metric].push(value)

    def report(self) -> dict[str, dict[str, float]]:
        return {metric: tracker.stats() for metric, tracker in self._trackers.items()}

    def totals(self) -> dict[str, float]:
        return {metric: tracker.stats()["count"] for metric, tracker in self._trackers.items()}

    def reset(self) -> None:
        self._trackers = {m: StatTracker() for m in self.METRICS}
