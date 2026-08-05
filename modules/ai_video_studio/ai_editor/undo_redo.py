"""Undo/redo manager — bounded history of deep-copied timeline snapshots."""
from __future__ import annotations

import copy
from typing import Any

from modules.ai_video_studio.editor_common import UndoStack, make_logger

logger = make_logger("editor.history")


class UndoRedoManager:
    """Snapshots the timeline before edits; undo/redo restore deep copies."""

    def __init__(self, limit: int = 100) -> None:
        self._stack = UndoStack(limit=limit)

    def push(self, state: dict[str, Any]) -> None:
        self._stack.push(copy.deepcopy(state))

    def undo(self) -> dict[str, Any] | None:
        restored = self._stack.undo()
        return copy.deepcopy(restored) if restored is not None else None

    def redo(self) -> dict[str, Any] | None:
        restored = self._stack.redo()
        return copy.deepcopy(restored) if restored is not None else None

    @property
    def can_undo(self) -> bool:
        return self._stack.can_undo

    @property
    def can_redo(self) -> bool:
        return self._stack.can_redo

    def clear(self) -> None:
        self._stack.clear()
