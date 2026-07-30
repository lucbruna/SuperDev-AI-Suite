from __future__ import annotations

from typing import Any, Dict, List, Optional


class TaskAllocator:
    """Allocates tasks to agents."""

    def __init__(self) -> None:
        self._allocations: Dict[str, str] = {}
        self._allocation_count: int = 0

    @property
    def allocation_count(self) -> int:
        return self._allocation_count

    def assign(self, task: Dict[str, Any], agents: List[str]) -> Optional[str]:
        if not agents:
            return None
        agent_id = agents[self._allocation_count % len(agents)]
        task_id = task.get("id", f"t{self._allocation_count}")
        self._allocations[task_id] = agent_id
        self._allocation_count += 1
        return agent_id

    def get_agent_for_task(self, task_id: str) -> Optional[str]:
        return self._allocations.get(task_id)

    def clear(self) -> None:
        self._allocations.clear()
        self._allocation_count = 0

    def to_dict(self) -> Dict[str, Any]:
        return {"allocations": dict(self._allocations), "count": self._allocation_count}
