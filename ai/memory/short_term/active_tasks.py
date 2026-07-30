from __future__ import annotations

import time
from typing import Any, Dict, List, Optional


class ActiveTask:
    """A task currently tracked in short-term memory."""

    def __init__(self, task_id: str, name: str, status: str = "pending", metadata: Dict[str, Any] | None = None):
        self._task_id = task_id
        self._name = name
        self._status = status
        self._metadata = metadata or {}
        self._created_at = time.time()

    @property
    def task_id(self) -> str:
        return self._task_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, value: str) -> None:
        self._status = value

    @property
    def metadata(self) -> Dict[str, Any]:
        return dict(self._metadata)

    @property
    def created_at(self) -> float:
        return self._created_at

    @property
    def age(self) -> float:
        return time.time() - self._created_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self._task_id,
            "name": self._name,
            "status": self._status,
            "metadata": dict(self._metadata),
            "created_at": self._created_at,
        }


class ActiveTasks:
    """Registry of currently active tasks."""

    def __init__(self):
        self._tasks: Dict[str, ActiveTask] = {}

    @property
    def count(self) -> int:
        return len(self._tasks)

    def register(self, task_id: str, name: str, metadata: Dict[str, Any] | None = None) -> ActiveTask:
        task = ActiveTask(task_id, name, metadata=metadata)
        self._tasks[task_id] = task
        return task

    def get(self, task_id: str) -> ActiveTask | None:
        return self._tasks.get(task_id)

    def update_status(self, task_id: str, status: str) -> bool:
        task = self._tasks.get(task_id)
        if task is None:
            return False
        task.status = status
        return True

    def complete(self, task_id: str) -> bool:
        return self.update_status(task_id, "completed")

    def fail(self, task_id: str) -> bool:
        return self.update_status(task_id, "failed")

    def remove(self, task_id: str) -> bool:
        return self._tasks.pop(task_id, None) is not None

    def list_active(self) -> List[ActiveTask]:
        return [t for t in self._tasks.values() if t.status in ("pending", "running")]

    def list_by_status(self, status: str) -> List[ActiveTask]:
        return [t for t in self._tasks.values() if t.status == status]

    def clear(self) -> None:
        self._tasks.clear()

    def to_dict_list(self) -> List[Dict[str, Any]]:
        return [t.to_dict() for t in self._tasks.values()]
