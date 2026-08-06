"""Long-term lessons — memory of past failures that feeds future plans.

When a phase fails (tests blocked a bad fix, reviewer rejected a change),
the runtime records a :class:`Lesson`. Later planning runs over the same
kind of goal read those lessons back and surface them as context, so the
brain (LLM) can avoid repeating the same mistake. Lessons are deduplicated
per (phase, goal) and bounded.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any

__all__ = ["Lesson", "LessonLearner", "LessonStore", "format_lessons"]

_PHASE_HINTS = {
    "plan": "the plan was not actionable",
    "implement": "the file changes were rejected or invalid",
    "test": "the generated code did not pass the project tests",
    "review": "the reviewer rejected the change",
    "merge": "the change could not be merged safely",
}


@dataclass(slots=True)
class Lesson:
    """One recorded failure and the guidance it implies."""

    phase: str
    goal: str
    error: str
    pattern: str = ""
    lesson: str = ""
    session_id: str = ""
    created_at: float = field(default_factory=time.time)
    lesson_id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])

    @property
    def key(self) -> str:
        """Dedupe key: same phase + goal."""
        return f"{self.phase}:{self.goal.strip().lower()}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "lesson_id": self.lesson_id,
            "phase": self.phase,
            "goal": self.goal,
            "error": self.error,
            "pattern": self.pattern,
            "lesson": self.lesson,
            "session_id": self.session_id,
            "created_at": round(self.created_at, 3),
        }


class LessonStore:
    """Bounded, deduplicated collection of lessons."""

    def __init__(self, max_lessons: int = 100) -> None:
        self.max_lessons = max_lessons
        self._lessons: dict[str, Lesson] = {}

    def add(self, lesson: Lesson) -> bool:
        """Store a lesson; ``False`` when a duplicate already exists."""
        if lesson.key in self._lessons:
            return False
        self._lessons[lesson.key] = lesson
        while len(self._lessons) > self.max_lessons:
            oldest = min(self._lessons.values(), key=lambda item: item.created_at)
            del self._lessons[oldest.key]
        return True

    def for_goal(self, goal: str) -> list[Lesson]:
        """Lessons whose goal overlaps with ``goal`` (token match)."""
        if not goal:
            return []
        tokens = {token.lower() for token in goal.split() if len(token) > 2}
        return [
            lesson
            for lesson in self._lessons.values()
            if any(token in lesson.goal.lower() for token in tokens)
        ]

    def all(self) -> list[Lesson]:
        return list(self._lessons.values())

    def clear(self) -> None:
        self._lessons.clear()

    def stats(self) -> dict[str, Any]:
        return {"lessons": len(self._lessons), "capacity": self.max_lessons}


def format_lessons(lessons: list[Lesson], limit: int = 5) -> str:
    """Human/LLM-readable context block for a planning prompt."""
    if not lessons:
        return ""
    lines = ["Previous failures to avoid (from earlier sessions):"]
    for lesson in lessons[:limit]:
        lines.append(
            f"- [{lesson.phase}] {lesson.goal.strip()} — "
            f"{lesson.lesson or lesson.error}"
        )
    return "\n".join(lines)


class LessonLearner:
    """Extracts lessons from ``task.failed`` events."""

    def on_task_failed(self, event: dict[str, Any], ctx) -> None:
        phase = event.get("phase", "")
        goal = event.get("goal", "")
        error = event.get("error", "")
        session_id = event.get("session_id", "")
        hint = _PHASE_HINTS.get(phase, "a phase of the loop failed")
        lesson = Lesson(
            phase=phase,
            goal=goal,
            error=error[:500],
            pattern=phase,
            lesson=f"Last run failed at {phase}: {hint} ({error[:200]})",
            session_id=session_id,
        )
        added = ctx.lessons.add(lesson)
        if added:
            ctx.publish(
                "lesson.recorded",
                {"phase": phase, "goal": goal, "lesson_id": lesson.lesson_id},
            )
