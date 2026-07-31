from __future__ import annotations

from typing import Any

from .episodes import Episodes
from .event_store import EventStore
from .execution_history import ExecutionHistory
from .experience import Experience
from .planner_history import PlannerHistory
from .reasoning_history import ReasoningHistory
from .recovery_history import RecoveryHistory
from .timeline import Timeline
from .workflow_history import WorkflowHistory


class EpisodicMemory:
    """High-level facade for episodic memory — AI lived experiences."""

    def __init__(self):
        self._event_store = EventStore()
        self._timeline = Timeline()
        self._episodes = Episodes()
        self._experiences: list[Experience] = []
        self._execution = ExecutionHistory()
        self._workflows = WorkflowHistory()
        self._plans = PlannerHistory()
        self._reasoning = ReasoningHistory()
        self._recovery = RecoveryHistory()

    @property
    def event_store(self) -> EventStore:
        return self._event_store

    @property
    def timeline(self) -> Timeline:
        return self._timeline

    @property
    def episodes(self) -> Episodes:
        return self._episodes

    @property
    def execution(self) -> ExecutionHistory:
        return self._execution

    @property
    def workflows(self) -> WorkflowHistory:
        return self._workflows

    @property
    def plans(self) -> PlannerHistory:
        return self._plans

    @property
    def reasoning(self) -> ReasoningHistory:
        return self._reasoning

    @property
    def recovery(self) -> RecoveryHistory:
        return self._recovery

    def record_event(self, event_type: str, data: dict[str, Any]) -> None:
        self._event_store.store(event_type, data)
        self._timeline.add(event_type, data)

    def record_experience(self, experience: Experience) -> None:
        self._experiences.append(experience)
        self._timeline.add("experience", {"id": experience.experience_id, "summary": experience.summary})

    def get_recent_experiences(self, count: int = 10) -> list[Experience]:
        return list(self._experiences[-count:])

    def search_experiences(self, query: str) -> list[Experience]:
        q = query.lower()
        return [e for e in self._experiences if q in e.summary.lower()]

    def snapshot(self) -> dict[str, Any]:
        return {
            "events": self._event_store.count,
            "timeline_entries": self._timeline.count,
            "episodes": self._episodes.count,
            "experiences": len(self._experiences),
            "executions": self._execution.count,
            "workflows": self._workflows.count,
            "plans": self._plans.count,
            "reasoning_traces": self._reasoning.count,
            "recoveries": self._recovery.count,
        }
