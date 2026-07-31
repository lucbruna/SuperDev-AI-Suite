"""Task engine: tarefas colaborativas.

Fluxo de uma solicitação "Criar aplicativo de vendas":
Planner -> Task Manager -> Coder -> Human Developer revisa ->
Security -> Testing -> Deploy, com agentes de IA como executores.
"""

from __future__ import annotations

from typing import Any

from collaboration.collaboration_config import CollaborationConfig
from collaboration.collaboration_events import (CollaborationEventType,
                                                CollaborationEvents)
from collaboration.collaboration_logger import get_logger
from collaboration.collaboration_metrics import CollaborationMetrics
from collaboration.collaboration_models import (MemberRecord, TaskPriority,
                                                TaskRecord, TaskStatus)
from collaboration.collaboration_registry import CollaborationRegistry
from collaboration.collaboration_security import CollaborationSecurity
from collaboration.tasks.task_manager import TaskManager
from collaboration.tasks.task_status import describe as status_options


class TaskEngine:
    """Orquestrador de tarefas (Fase 4 do Volume 26)."""

    def __init__(self, events: CollaborationEvents | None = None,
                 metrics: CollaborationMetrics | None = None,
                 config: CollaborationConfig | None = None,
                 security: CollaborationSecurity | None = None,
                 registry: CollaborationRegistry | None = None,
                 manager: TaskManager | None = None) -> None:
        self._log = get_logger()
        self.events = events or CollaborationEvents()
        self.metrics = metrics or CollaborationMetrics()
        self.config = config or CollaborationConfig()
        self.security = security or CollaborationSecurity()
        self.manager = manager or TaskManager(registry=registry)

    def create(self, project_id: str, workspace_id: str, title: str,
               description: str = "",
               priority: TaskPriority = TaskPriority.MEDIUM,
               assignee_id: str = "",
               status: TaskStatus = TaskStatus.TODO,
               **extra: Any) -> TaskRecord:
        task = self.manager.create(project_id, workspace_id, title,
                                   description, priority, assignee_id,
                                   status, **extra)
        self.metrics.increment("collab.tasks")
        self.events.publish(CollaborationEventType.TASK_CREATED,
                            {"task_id": task.task_id, "title": title,
                             "project_id": project_id})
        self.manager.activity_log.for_task(task.task_id).record(
            "task.created", assignee_id or workspace_id)
        return task

    def get(self, task_id: str) -> TaskRecord | None:
        return self.manager.get(task_id)

    def list(self) -> list[str]:
        return self.manager.list()

    def remove(self, task_id: str) -> bool:
        return self.manager.remove(task_id)

    def by_project(self, project_id: str) -> list[TaskRecord]:
        return self.manager.by_project(project_id)

    def ordered(self) -> list[TaskRecord]:
        return self.manager.ordered()

    def assign(self, task_id: str, member: MemberRecord,
               priority: TaskPriority | None = None) -> str:
        if priority is None:
            task = self.get(task_id)
            priority = task.priority if task is not None else \
                TaskPriority.MEDIUM
        assignee_id = self.manager.scheduler.assign(task_id, member,
                                                    priority)
        self.manager.set_assignee(task_id, assignee_id)
        self.events.publish(CollaborationEventType.TASK_ASSIGNED,
                            {"task_id": task_id, "assignee_id": assignee_id})
        self.manager.activity_log.for_task(task_id).record(
            "task.assigned", assignee_id)
        return assignee_id

    def update_status(self, task_id: str, status: TaskStatus,
                      force: bool = False) -> TaskRecord | None:
        task = self.manager.set_status(task_id, status, force)
        if task is not None:
            self.events.publish(CollaborationEventType.TASK_UPDATED,
                                {"task_id": task_id, "status": status.value})
            if status == TaskStatus.DONE:
                self.events.publish(CollaborationEventType.TASK_COMPLETED,
                                    {"task_id": task_id})
            self.manager.activity_log.for_task(task_id).record(
                "task.status", task_id, {"status": status.value})
        return task

    def add_dependency(self, task_id: str, depends_on: str) -> None:
        self.manager.dependencies.add(task_id, depends_on)

    def ready(self, task_id: str) -> bool:
        done = {t.task_id for t in self.manager.by_project_ordered()
                if t.status == TaskStatus.DONE}
        return self.manager.dependencies.ready(task_id, done)

    def blockers(self, task_id: str) -> list[str]:
        return self.manager.dependencies.blockers(task_id)

    def scheduler(self) -> Any:
        return self.manager.scheduler

    def status_options(self, status: TaskStatus) -> list[str]:
        return status_options(status)

    def activity(self, task_id: str,
                 limit: int = 50) -> list[dict[str, Any]]:
        return self.manager.activity_log.for_task(task_id).list(limit)

    def stats(self) -> dict[str, Any]:
        return {"tasks": self.manager.count()}
