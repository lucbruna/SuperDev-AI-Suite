"""Task dependencies."""

from __future__ import annotations

from typing import Any


class TaskDependencies:
    """Tracks which tasks block other tasks."""

    def __init__(self) -> None:
        self._depends_on: dict[str, list[str]] = {}
        self._blocks: dict[str, list[str]] = {}

    def add(self, task_id: str, depends_on: str) -> None:
        self._depends_on.setdefault(task_id, [])
        if depends_on not in self._depends_on[task_id]:
            self._depends_on[task_id].append(depends_on)
        self._blocks.setdefault(depends_on, [])
        if task_id not in self._blocks[depends_on]:
            self._blocks[depends_on].append(task_id)

    def blockers(self, task_id: str) -> list[str]:
        return list(self._depends_on.get(task_id, []))

    def blocked_by(self, task_id: str) -> list[str]:
        """Tasks blocked by the given task."""
        return list(self._blocks.get(task_id, []))

    def is_blocked(self, task_id: str) -> bool:
        return bool(self._depends_on.get(task_id))

    def ready(self, task_id: str, done_ids: set[str]) -> bool:
        blockers = self._depends_on.get(task_id, [])
        return all(blocker in done_ids for blocker in blockers)

    def remove(self, task_id: str) -> None:
        self._depends_on.pop(task_id, None)
        for key, values in self._blocks.items():
            if task_id in values:
                values.remove(task_id)

    def to_dict(self) -> dict[str, Any]:
        return {"depends_on": {k: list(v)
                               for k, v in self._depends_on.items()},
                "blocks": {k: list(v) for k, v in self._blocks.items()}}
