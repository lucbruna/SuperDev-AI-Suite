from __future__ import annotations

import uuid
from enum import IntEnum

from pydantic import BaseModel


class Complexity(IntEnum):
    TRIVIAL = 1
    EASY = 2
    MEDIUM = 3
    HARD = 4
    COMPLEX = 5


class Task(BaseModel):
    id: str = ""
    title: str = ""
    description: str = ""
    complexity: Complexity = Complexity.MEDIUM
    estimated_effort: float = 1.0
    status: str = "pending"


class TaskBreakdown:
    def __init__(self) -> None:
        self._tasks: list[Task] = []

    async def break_down(self, goal: str) -> list[Task]:
        self._tasks = self._parse_goal(goal)
        return self._tasks

    def _parse_goal(self, goal: str) -> list[Task]:
        tasks: list[Task] = []
        lines = [l.strip() for l in goal.split("\n") if l.strip()]
        for line in lines:
            task = Task(
                id=str(uuid.uuid4()),
                title=line[:50],
                description=line,
                complexity=self._estimate_complexity(line),
                estimated_effort=self._estimate_effort(line),
                status="pending",
            )
            tasks.append(task)
        return tasks

    def _estimate_complexity(self, text: str) -> Complexity:
        length = len(text)
        if length < 20:
            return Complexity.TRIVIAL
        elif length < 50:
            return Complexity.EASY
        elif length < 100:
            return Complexity.MEDIUM
        elif length < 200:
            return Complexity.HARD
        return Complexity.COMPLEX

    def _estimate_effort(self, text: str) -> float:
        return max(0.5, len(text) / 100)

    def get_tasks(self) -> list[Task]:
        return self._tasks
