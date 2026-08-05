"""TaskBuilder: converts decomposition specs into validated Task objects."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from aios.planning.decomposer import TaskSpec

TASK_STATUSES = ("pending", "ready", "running", "completed", "failed", "skipped", "cancelled")


@dataclass
class Task:
    task_id: str
    name: str
    kind: str = "action"
    description: str = ""
    status: str = "pending"
    agent: str | None = None
    params: dict[str, Any] = field(default_factory=dict)
    depends_on: list[str] = field(default_factory=list)
    priority: int = 5
    estimated_duration: float = 1.0
    resource: str | None = None
    start_time: float | None = None
    end_time: float | None = None
    result: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_ready(self, completed: set[str] | None = None) -> bool:
        """True when pending and every dependency has completed."""
        if self.status not in ("pending", "skipped"):
            return False
        done = set(completed or ())
        return all(dep in done for dep in self.depends_on)


class TaskBuilder:
    """Deterministic task factory with stable sequential ids."""

    def __init__(self) -> None:
        self._seq = 0

    def _next_id(self) -> str:
        self._seq += 1
        return f"task-{self._seq:04d}"

    def build(self, spec: TaskSpec | None = None, **overrides: Any) -> Task:
        """Build a single task. Dependency names are NOT resolved by id here;
        use :meth:`build_many` for name-to-id resolution."""
        task_id = overrides.pop("task_id", self._next_id())
        if spec is not None:
            base: dict[str, Any] = {
                "task_id": task_id,
                "name": spec.name,
                "kind": spec.kind,
                "description": spec.description,
                "agent": spec.agent,
                "params": dict(spec.params),
                "depends_on": list(spec.depends_on),
                "priority": spec.priority,
                "estimated_duration": spec.estimated_duration,
                "metadata": {"strategy": spec.strategy},
            }
        else:
            base = {"task_id": task_id, "name": overrides.pop("name", f"task-{task_id}")}
        base.update(overrides)
        return Task(**base)

    def build_many(self, specs: list[TaskSpec]) -> list[Task]:
        """Build tasks and resolve ``depends_on`` names to task ids."""
        self._seq = 0
        tasks: list[Task] = []
        by_name: dict[str, Task] = {}
        for spec in specs:
            task = self.build(spec)
            tasks.append(task)
            by_name[spec.name] = task
        for spec, task in zip(specs, tasks):
            resolved = [by_name[name].task_id for name in spec.depends_on if name in by_name]
            task.depends_on = resolved
        return tasks

    @staticmethod
    def validate(task: Task) -> list[str]:
        """Return a list of validation problems (empty when valid)."""
        problems: list[str] = []
        if not task.name or not str(task.name).strip():
            problems.append("task name must be non-empty")
        if task.status not in TASK_STATUSES:
            problems.append(f"invalid status {task.status!r}")
        if not 1 <= int(task.priority) <= 10:
            problems.append("priority must be between 1 and 10")
        if task.estimated_duration < 0:
            problems.append("estimated_duration must be >= 0")
        if task.task_id in task.depends_on:
            problems.append("task cannot depend on itself")
        return problems
