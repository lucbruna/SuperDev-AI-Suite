from __future__ import annotations

from typing import Any, Dict, List, Tuple


class PriorityManager:
    """Manages task priority levels."""

    def __init__(self) -> None:
        self._priorities: Dict[str, int] = {}

    def set_priority(self, task_id: str, priority: int) -> None:
        self._priorities[task_id] = priority

    def get_priority(self, task_id: str) -> int:
        return self._priorities.get(task_id, 0)

    def sorted_tasks(self) -> List[Tuple[str, int]]:
        return sorted(self._priorities.items(), key=lambda x: x[1], reverse=True)

    def remove(self, task_id: str) -> bool:
        return self._priorities.pop(task_id, None) is not None

    def clear(self) -> None:
        self._priorities.clear()

    def to_dict(self) -> Dict[str, Any]:
        return {"priorities": dict(self._priorities)}
