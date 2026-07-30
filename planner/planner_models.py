from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum, IntEnum
from typing import Any

from pydantic import BaseModel, Field


class TaskPriority(IntEnum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    CRITICAL = 3


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"


class TaskDependency(BaseModel):
    from_task: str
    to_task: str
    dependency_type: str = "finish_to_start"


class Task(BaseModel):
    name: str
    description: str = ""
    priority: TaskPriority = TaskPriority.MEDIUM
    status: str = "pending"
    category: str = "general"
    estimated_duration: float = 60.0
    metadata: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)
    dependencies: list[TaskDependency] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())

    async def execute(self) -> dict[str, Any]:
        return {"task": self.name, "status": "completed"}


class Plan(BaseModel):
    goal: str
    tasks: list[Task] = Field(default_factory=list)
    category: str = "general"
    context: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime | None = None
    updated_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def id(self) -> str:
        return f"plan_{hash(self.goal) & 0xFFFFFFFF:08x}"

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def remove_task(self, task_name: str) -> None:
        self.tasks = [t for t in self.tasks if t.name != task_name]

    def get_task(self, name: str) -> Task | None:
        for task in self.tasks:
            if task.name == name:
                return task
        return None


class PlannerConfig(BaseModel):
    max_tasks_per_plan: int = 50
    default_timeout: int = 300
    max_concurrent_tasks: int = 5
    enable_optimization: bool = True
    enable_validation: bool = True
    log_level: str = "INFO"
    storage_backend: str = "memory"
