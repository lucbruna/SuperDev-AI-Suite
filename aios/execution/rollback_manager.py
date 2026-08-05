"""RollbackManager: undo log with compensation handlers for executed actions."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class RollbackEntry:
    action_id: str
    name: str
    target: str
    undo: Callable[[], None] | None = None
    payload: Any = None
    committed: bool = False


class RollbackManager:
    """Append-only undo log. ``rollback`` unwinds entries in reverse order."""

    def __init__(self) -> None:
        self._entries: list[RollbackEntry] = []
        self._seq = 0

    def record(self, name: str, target: str, undo: Callable[[], None] | None = None, payload: Any = None) -> str:
        self._seq += 1
        action_id = f"rb-{self._seq:04d}"
        self._entries.append(
            RollbackEntry(action_id=action_id, name=name, target=target, undo=undo, payload=payload)
        )
        return action_id

    def commit(self, action_id: str) -> bool:
        entry = self._find(action_id)
        if entry is None:
            return False
        entry.committed = True
        return True

    def rollback(self, action_id: str | None = None) -> list[str]:
        """Undo entries from the tail back to (and including) ``action_id``.
        Without ``action_id``, unwinds the entire log."""
        if action_id is None:
            return self.undo_all()
        target = self._find(action_id)
        if target is None:
            return []
        index = self._entries.index(target)
        undone: list[str] = []
        for entry in reversed(self._entries[index:]):
            if not entry.committed and entry.undo is not None:
                entry.undo()
            undone.append(entry.action_id)
        del self._entries[index:]
        return undone

    def undo_all(self) -> list[str]:
        undone: list[str] = []
        while self._entries:
            entry = self._entries.pop()
            if not entry.committed and entry.undo is not None:
                entry.undo()
            undone.append(entry.action_id)
        return undone

    def entries(self) -> list[RollbackEntry]:
        return list(self._entries)

    def _find(self, action_id: str) -> RollbackEntry | None:
        return next((e for e in self._entries if e.action_id == action_id), None)
