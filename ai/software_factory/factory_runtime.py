"""Factory Runtime - Execution runtime for factory operations."""
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import hashlib


class TaskState(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class FactoryTask:
    task_id: str
    project_id: str
    name: str
    state: TaskState = TaskState.PENDING
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    error: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class FactoryRuntime:
    def __init__(self):
        self.tasks: Dict[str, FactoryTask] = {}
        self.handlers: Dict[str, Callable] = {}
        self.task_log: List[Dict[str, Any]] = []

    def submit_task(self, project_id: str, name: str, input_data: Dict[str, Any] = None) -> FactoryTask:
        task_id = hashlib.sha256(f"{project_id}{name}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        task = FactoryTask(task_id=task_id, project_id=project_id, name=name, input_data=input_data or {})
        self.tasks[task_id] = task
        return task

    def execute_task(self, task_id: str) -> bool:
        task = self.tasks.get(task_id)
        if not task:
            return False
        task.state = TaskState.RUNNING
        task.started_at = datetime.now()
        handler = self.handlers.get(task.name)
        if handler:
            try:
                result = handler(task.input_data)
                task.output_data = result if isinstance(result, dict) else {"result": result}
                task.state = TaskState.COMPLETED
                task.completed_at = datetime.now()
                self._log(task)
                return True
            except Exception as e:
                task.state = TaskState.FAILED
                task.error = str(e)
                task.completed_at = datetime.now()
                self._log(task)
                return False
        task.state = TaskState.COMPLETED
        task.completed_at = datetime.now()
        self._log(task)
        return True

    def register_handler(self, task_name: str, handler: Callable) -> None:
        self.handlers[task_name] = handler

    def get_task(self, task_id: str) -> Optional[FactoryTask]:
        return self.tasks.get(task_id)

    def get_project_tasks(self, project_id: str) -> List[FactoryTask]:
        return [t for t in self.tasks.values() if t.project_id == project_id]

    def cancel_task(self, task_id: str) -> bool:
        task = self.tasks.get(task_id)
        if task and task.state == TaskState.PENDING:
            task.state = TaskState.CANCELLED
            return True
        return False

    def count(self) -> int:
        return len(self.tasks)

    def _log(self, task: FactoryTask):
        self.task_log.append({"task_id": task.task_id, "project_id": task.project_id, "name": task.name, "state": task.state.value, "timestamp": datetime.now().isoformat()})
