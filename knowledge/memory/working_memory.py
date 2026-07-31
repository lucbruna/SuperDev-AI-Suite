from __future__ import annotations

import logging
from collections import OrderedDict
from typing import Any


class WorkingMemory:
    """Short-lived scratchpad for the active task, automatically cleared on completion."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.knowledge.memory.working")
        self._slots: OrderedDict[str, Any] = OrderedDict()
        self._task: str | None = None

    def begin_task(self, task: str) -> None:
        self._task = task
        self._slots.clear()

    def set(self, key: str, value: Any) -> None:
        self._slots[key] = value
        self._slots.move_to_end(key)

    def get(self, key: str, default: Any = None) -> Any:
        if key in self._slots:
            self._slots.move_to_end(key)
            return self._slots[key]
        return default

    def clear(self) -> None:
        self._slots.clear()

    def end_task(self) -> dict[str, Any]:
        snapshot = dict(self._slots)
        self._slots.clear()
        self._task = None
        return snapshot

    def current_task(self) -> str | None:
        return self._task

    def snapshot(self) -> dict[str, Any]:
        return dict(self._slots)
