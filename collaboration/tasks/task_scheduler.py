"""Task scheduling (incl. AI agent assignment)."""

from __future__ import annotations

from typing import Any

from collaboration.collaboration_models import MemberRecord, TaskPriority
from collaboration.tasks.task_priorities import priority_rank


class TaskScheduler:
    """Assigns tasks to members/agents based on load and skills."""

    def __init__(self) -> None:
        self._load: dict[str, int] = {}

    def register_member(self, member: MemberRecord) -> None:
        if member.member_id not in self._load:
            self._load[member.member_id] = 0

    def assign(self, task_id: str, member: MemberRecord,
               priority: TaskPriority = TaskPriority.MEDIUM) -> str:
        self.register_member(member)
        self._load[member.member_id] += 1 + priority_rank(priority)
        return member.member_id

    def unassign(self, member_id: str) -> None:
        if member_id in self._load:
            self._load[member_id] = max(0, self._load[member_id] - 1)

    def load_of(self, member_id: str) -> int:
        return self._load.get(member_id, 0)

    def least_loaded(self, members: list[MemberRecord],
                     required_skill: str | None = None) -> MemberRecord | None:
        candidates = members
        if required_skill:
            candidates = [m for m in members
                          if required_skill in (m.skills or [])]
        if not candidates:
            return None
        return min(candidates, key=lambda m: self.load_of(m.member_id))

    def capacity(self, member_id: str, max_load: int = 5) -> bool:
        return self.load_of(member_id) < max_load

    def snapshot(self) -> dict[str, Any]:
        return dict(self._load)
