"""Experience store: execution outcomes for reuse (Volume 31)."""

from __future__ import annotations

from agent_orchestration.orchestrator_models import ExecutionResult, TaskStatus
from agent_orchestration.orchestrator_protocols import now


class ExperienceStore:
    """Records execution results so agents can learn from past runs."""

    def __init__(self) -> None:
        self._experiences: list[dict] = []

    def record(self, result: ExecutionResult) -> dict:
        experience = {
            "result_id": result.result_id,
            "task_id": result.task_id,
            "agent_id": result.agent_id,
            "status": result.status.value,
            "output": result.output,
            "error": result.error,
            "duration": result.duration,
            "created_at": now(),
        }
        self._experiences.append(experience)
        return experience

    def by_agent(self, agent_id: str) -> list[dict]:
        return [exp for exp in self._experiences
                if exp["agent_id"] == agent_id]

    def success_rate(self, agent_id: str | None = None) -> float:
        experiences = (self.by_agent(agent_id) if agent_id
                       else self._experiences)
        if not experiences:
            return 0.0
        completed = sum(1 for exp in experiences
                        if exp["status"] == TaskStatus.COMPLETED.value)
        return completed / len(experiences)

    def average_duration(self, agent_id: str | None = None) -> float:
        experiences = (self.by_agent(agent_id) if agent_id
                       else self._experiences)
        if not experiences:
            return 0.0
        return sum(exp["duration"] for exp in experiences) / len(experiences)

    def count(self, agent_id: str | None = None) -> int:
        return len(self.by_agent(agent_id)) if agent_id else len(
            self._experiences)

    def all(self) -> list[dict]:
        return list(self._experiences)
