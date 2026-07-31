"""Memory subsystem facade (Volume 31)."""

from __future__ import annotations

from typing import Any

from agent_orchestration.memory.agent_memory import AgentMemory
from agent_orchestration.memory.experience_store import ExperienceStore
from agent_orchestration.memory.lesson_manager import LessonManager
from agent_orchestration.memory.long_memory import LongMemory
from agent_orchestration.memory.short_memory import ShortMemory
from agent_orchestration.orchestrator_events import (OrchestratorEvents,
                                                     OrchestratorEventType)
from agent_orchestration.orchestrator_metrics import OrchestratorMetrics
from agent_orchestration.orchestrator_models import ExecutionResult, Lesson


class MemoryEngine:
    """Facade over working, short-term, long-term and experience memory."""

    def __init__(self, agent_memory: AgentMemory | None = None,
                 short: ShortMemory | None = None,
                 long: LongMemory | None = None,
                 experiences: ExperienceStore | None = None,
                 lessons: LessonManager | None = None,
                 events: OrchestratorEvents | None = None,
                 metrics: OrchestratorMetrics | None = None) -> None:
        self.agent_memory = agent_memory or AgentMemory()
        self.short = short or ShortMemory()
        self.long = long or LongMemory()
        self.experiences = experiences or ExperienceStore()
        self.lessons = lessons or LessonManager()
        self.events = events or OrchestratorEvents()
        self.metrics = metrics or OrchestratorMetrics()

    def remember(self, agent_id: str, key: str, value: Any) -> None:
        self.agent_memory.remember(agent_id, key, value)
        self.metrics.increment("ao.memory_facts")

    def recall(self, agent_id: str, key: str, default: Any = None) -> Any:
        return self.agent_memory.recall(agent_id, key, default)

    def recent(self, agent_id: str, limit: int = 10) -> list[dict]:
        return self.short.recent(agent_id, limit)

    def remember_long(self, agent_id: str, key: str, value: Any,
                      importance: float = 0.5) -> None:
        self.long.remember(agent_id, key, value, importance)

    def search_long(self, agent_id: str, term: str) -> list[dict]:
        return self.long.search(agent_id, term)

    def record_experience(self, result: ExecutionResult) -> None:
        self.experiences.record(result)
        self.metrics.increment("ao.experiences")

    def success_rate(self, agent_id: str | None = None) -> float:
        return self.experiences.success_rate(agent_id)

    def record_lesson(self, agent_id: str, topic: str, error: str,
                      solution: str) -> Lesson:
        lesson = self.lessons.record(agent_id, topic, error, solution)
        self.metrics.increment("ao.lessons")
        self.events.publish(OrchestratorEventType.LESSON_LEARNED,
                            {"lesson_id": lesson.lesson_id,
                             "agent_id": agent_id, "topic": topic})
        return lesson

    def stats(self) -> dict[str, Any]:
        return {
            "facts": self.agent_memory.count(),
            "short_total": self.short.total(),
            "long_total": self.long.count(),
            "experiences": self.experiences.count(),
            "lessons": self.lessons.count(),
            "lessons_applied": self.lessons.applied_count(),
        }
