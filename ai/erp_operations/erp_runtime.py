"""ERP Runtime — Execution runtime for ERP operations."""
import hashlib
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ERPTaskState(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ERPTask:
    task_id: str
    project_id: str
    name: str
    state: ERPTaskState = ERPTaskState.PENDING
    input_data: dict[str, Any] = field(default_factory=dict)
    output_data: dict[str, Any] = field(default_factory=dict)
    error: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    started_at: datetime | None = None
    completed_at: datetime | None = None


class ERPRuntime:
    def __init__(self):
        self.tasks: dict[str, ERPTask] = {}
        self.handlers: dict[str, Callable] = {}
        self.task_log: list[dict[str, Any]] = []

    def submit_task(self, project_id: str, name: str, input_data: dict[str, Any] | None = None) -> ERPTask:
        task_id = hashlib.sha256(f"{project_id}{name}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        task = ERPTask(task_id=task_id, project_id=project_id, name=name, input_data=input_data or {})
        self.tasks[task_id] = task
        return task

    def execute_task(self, task_id: str) -> bool:
        task = self.tasks.get(task_id)
        if not task:
            return False
        task.state = ERPTaskState.RUNNING
        task.started_at = datetime.now()
        handler = self.handlers.get(task.name)
        if handler:
            try:
                result = handler(task.input_data)
                task.output_data = result if isinstance(result, dict) else {"result": result}
                task.state = ERPTaskState.COMPLETED
                task.completed_at = datetime.now()
                self._log(task)
                return True
            except Exception as e:
                task.state = ERPTaskState.FAILED
                task.error = str(e)
                task.completed_at = datetime.now()
                self._log(task)
                return False
        task.state = ERPTaskState.COMPLETED
        task.completed_at = datetime.now()
        self._log(task)
        return True

    def register_handler(self, task_name: str, handler: Callable) -> None:
        self.handlers[task_name] = handler

    def get_task(self, task_id: str) -> ERPTask | None:
        return self.tasks.get(task_id)

    def cancel_task(self, task_id: str) -> bool:
        task = self.tasks.get(task_id)
        if task and task.state == ERPTaskState.PENDING:
            task.state = ERPTaskState.CANCELLED
            return True
        return False

    def count(self) -> int:
        return len(self.tasks)

    def _log(self, task: ERPTask) -> None:
        self.task_log.append({"task_id": task.task_id, "name": task.name, "state": task.state.value, "timestamp": datetime.now().isoformat()})
