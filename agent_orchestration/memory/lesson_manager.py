"""Lesson management for agent improvement (Volume 31)."""

from __future__ import annotations

from agent_orchestration.orchestrator_models import Lesson
from agent_orchestration.orchestrator_protocols import new_id, now


class LessonManager:
    """Records and tracks lessons learned from failures."""

    def __init__(self) -> None:
        self._lessons: list[Lesson] = []

    def record(self, agent_id: str, topic: str, error: str,
               solution: str) -> Lesson:
        lesson = Lesson(lesson_id=new_id("lesson"), agent_id=agent_id,
                        topic=topic, error=error, solution=solution,
                        applied=False, created_at=now())
        self._lessons.append(lesson)
        return lesson

    def list(self, agent_id: str | None = None) -> list[Lesson]:
        if agent_id is None:
            return list(self._lessons)
        return [lesson for lesson in self._lessons
                if lesson.agent_id == agent_id]

    def mark_applied(self, lesson_id: str) -> bool:
        for lesson in self._lessons:
            if lesson.lesson_id == lesson_id:
                lesson.applied = True
                return True
        return False

    def applied_count(self) -> int:
        return sum(1 for lesson in self._lessons if lesson.applied)

    def count(self) -> int:
        return len(self._lessons)
