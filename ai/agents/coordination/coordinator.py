from __future__ import annotations

from typing import Any, Dict, List, Optional

from .team_manager import TeamManager
from .task_allocator import TaskAllocator


class Coordinator:
    """Central coordinator for agent teams."""

    def __init__(self) -> None:
        self._team_manager = TeamManager()
        self._task_allocator = TaskAllocator()

    @property
    def team_manager(self) -> TeamManager:
        return self._team_manager

    @property
    def task_allocator(self) -> TaskAllocator:
        return self._task_allocator

    def assign_task(self, team_id: str, task: Dict[str, Any]) -> Optional[str]:
        members = self._team_manager.get_team(team_id)
        if not members:
            return None
        return self._task_allocator.assign(task, members)

    def get_status(self) -> Dict[str, Any]:
        return {
            "teams": self._team_manager.team_count,
            "allocations": self._task_allocator.allocation_count,
        }
