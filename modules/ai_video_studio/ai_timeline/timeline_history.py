"""Timeline history — undo/redo stack for timeline edits."""
from __future__ import annotations

import copy
from typing import Any



class TimelineHistory:
    """Snapshot-based undo/redo for timeline state."""

    def __init__(self, engine: Any | None = None, max_depth: int = 50) -> None:
        if engine is None:
            from modules.ai_video_studio.ai_timeline.timeline_engine import get_timeline_engine

            engine = get_timeline_engine()
        self.engine = engine
        self.max_depth = max_depth
        self._undo: list[dict[str, Any]] = []
        self._redo: list[dict[str, Any]] = []

    def snapshot(self) -> dict[str, Any]:
        return copy.deepcopy(self.engine.to_dict())

    def record(self) -> None:
        """Push the current state onto the undo stack."""
        self._undo.append(self.snapshot())
        if len(self._undo) > self.max_depth:
            self._undo.pop(0)
        self._redo.clear()

    def undo(self) -> dict[str, Any] | None:
        if not self._undo:
            return None
        current = self.snapshot()
        self._redo.append(current)
        state = self._undo.pop()
        self._apply(state)
        return state

    def redo(self) -> dict[str, Any] | None:
        if not self._redo:
            return None
        current = self.snapshot()
        self._undo.append(current)
        state = self._redo.pop()
        self._apply(state)
        return state

    def can_undo(self) -> bool:
        return bool(self._undo)

    def can_redo(self) -> bool:
        return bool(self._redo)

    def clear(self) -> None:
        self._undo.clear()
        self._redo.clear()

    def _apply(self, state: dict[str, Any]) -> None:
        self.engine.clips = copy.deepcopy(state.get("clips", []))
        self.engine.tracks = copy.deepcopy(state.get("tracks", {}))


_timeline_history: TimelineHistory | None = None


def get_timeline_history() -> TimelineHistory:
    global _timeline_history
    if _timeline_history is None:
        _timeline_history = TimelineHistory()
    return _timeline_history
