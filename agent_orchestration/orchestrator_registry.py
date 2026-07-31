"""Central registry for the Agent Orchestration Engine (Volume 31)."""

from __future__ import annotations

from typing import Any

from agent_orchestration.orchestrator_models import (AgentMessage, AgentProfile,
                                                     AgentTask,
                                                     EvaluationReport, Lesson)


class OrchestratorRegistry:
    """Public CRUD over agents, tasks, messages, reports and lessons."""

    def __init__(self) -> None:
        self._agents: dict[str, AgentProfile] = {}
        self._tasks: dict[str, AgentTask] = {}
        self._messages: dict[str, AgentMessage] = {}
        self._reports: dict[str, EvaluationReport] = {}
        self._lessons: dict[str, Lesson] = {}
        self._max_messages = 1000

    # -- agents --------------------------------------------------------------
    def register_agent(self, agent: AgentProfile) -> None:
        self._agents[agent.agent_id] = agent

    def get_agent(self, agent_id: str) -> AgentProfile | None:
        return self._agents.get(agent_id)

    def list_agents(self) -> list[AgentProfile]:
        return list(self._agents.values())

    def remove_agent(self, agent_id: str) -> bool:
        return self._agents.pop(agent_id, None) is not None

    def count_agents(self) -> int:
        return len(self._agents)

    # -- tasks ---------------------------------------------------------------
    def register_task(self, task: AgentTask) -> None:
        self._tasks[task.task_id] = task

    def get_task(self, task_id: str) -> AgentTask | None:
        return self._tasks.get(task_id)

    def list_tasks(self) -> list[AgentTask]:
        return list(self._tasks.values())

    def remove_task(self, task_id: str) -> bool:
        return self._tasks.pop(task_id, None) is not None

    def count_tasks(self) -> int:
        return len(self._tasks)

    # -- messages ------------------------------------------------------------
    def record_message(self, message: AgentMessage) -> None:
        self._messages[message.message_id] = message
        if len(self._messages) > self._max_messages:
            oldest = next(iter(self._messages))
            del self._messages[oldest]

    def get_message(self, message_id: str) -> AgentMessage | None:
        return self._messages.get(message_id)

    def list_messages(self) -> list[AgentMessage]:
        return list(self._messages.values())

    def count_messages(self) -> int:
        return len(self._messages)

    # -- evaluation reports --------------------------------------------------
    def record_report(self, report: EvaluationReport) -> None:
        self._reports[report.evaluation_id] = report

    def get_report(self, evaluation_id: str) -> EvaluationReport | None:
        return self._reports.get(evaluation_id)

    def list_reports(self) -> list[EvaluationReport]:
        return list(self._reports.values())

    def count_reports(self) -> int:
        return len(self._reports)

    # -- lessons -------------------------------------------------------------
    def record_lesson(self, lesson: Lesson) -> None:
        self._lessons[lesson.lesson_id] = lesson

    def get_lesson(self, lesson_id: str) -> Lesson | None:
        return self._lessons.get(lesson_id)

    def list_lessons(self) -> list[Lesson]:
        return list(self._lessons.values())

    def count_lessons(self) -> int:
        return len(self._lessons)

    # -- stats ---------------------------------------------------------------
    def stats(self) -> dict[str, Any]:
        return {
            "agents": self.count_agents(),
            "tasks": self.count_tasks(),
            "messages": self.count_messages(),
            "reports": self.count_reports(),
            "lessons": self.count_lessons(),
        }
