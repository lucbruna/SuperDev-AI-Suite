"""Priority assignment for tasks (Volume 31)."""

from __future__ import annotations

from agent_orchestration.orchestrator_models import AgentTask, Priority


class PriorityManager:
    """Derives a task priority from a normalized score or task hints."""

    @staticmethod
    def from_score(score: float) -> Priority:
        if score < 0.25:
            return Priority.LOW
        if score < 0.5:
            return Priority.MEDIUM
        if score < 0.75:
            return Priority.HIGH
        return Priority.CRITICAL

    @staticmethod
    def rank(priority: Priority) -> int:
        return priority.rank

    def decide(self, task: AgentTask, score: float) -> Priority:
        priority = self.from_score(score)
        task.priority = priority
        return priority

    @staticmethod
    def sort(tasks: list[AgentTask]) -> list[AgentTask]:
        return sorted(tasks, key=lambda task: task.priority.rank,
                      reverse=True)
