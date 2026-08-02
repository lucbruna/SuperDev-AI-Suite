from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class WorkflowStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class StepStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"


class StepType(StrEnum):
    CODE = "code"
    API_CALL = "api_call"
    CONDITION = "condition"
    PARALLEL = "parallel"
    LOOP = "loop"
    HUMAN_APPROVAL = "human_approval"
    TRANSFORM = "transform"
    WAIT = "wait"


@dataclass
class StepConfig:
    id: str
    name: str
    step_type: StepType
    config: dict[str, Any] = field(default_factory=dict)
    depends_on: list[str] = field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3
    timeout_seconds: int = 300
    continue_on_error: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dict (dataclass — no model_dump)."""
        return {
            "id": self.id,
            "name": self.name,
            "step_type": self.step_type.value if isinstance(self.step_type, StepType) else str(self.step_type),
            "config": self.config,
            "depends_on": self.depends_on,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "timeout_seconds": self.timeout_seconds,
            "continue_on_error": self.continue_on_error,
        }


@dataclass
class StepResult:
    step_id: str
    status: StepStatus
    output: Any = None
    error: str | None = None
    attempts: int = 0
    execution_time_ms: float = 0.0


@dataclass
class WorkflowDefinition:
    id: str
    name: str
    description: str = ""
    steps: list[StepConfig] = field(default_factory=list)
    variables: dict[str, Any] = field(default_factory=dict)
    version: int = 1
    tags: list[str] = field(default_factory=list)

    def get_step(self, step_id: str) -> StepConfig | None:
        for step in self.steps:
            if step.id == step_id:
                return step
        return None

    def get_dependencies(self, step_id: str) -> list[str]:
        step = self.get_step(step_id)
        return step.depends_on if step else []

    def get_root_steps(self) -> list[StepConfig]:
        return [s for s in self.steps if not s.depends_on]

    def validate(self) -> list[str]:
        errors = []
        step_ids = {s.id for s in self.steps}

        for step in self.steps:
            for dep in step.depends_on:
                if dep not in step_ids:
                    errors.append(f"Step '{step.id}' depends on unknown step '{dep}'")

        visited = set()
        visiting = set()

        def has_cycle(step_id: str) -> bool:
            if step_id in visiting:
                return True
            if step_id in visited:
                return False
            visiting.add(step_id)
            for dep in self.get_dependencies(step_id):
                if has_cycle(dep):
                    return True
            visiting.remove(step_id)
            visited.add(step_id)
            return False

        for step in self.steps:
            if has_cycle(step.id):
                errors.append(f"Cycle detected involving step '{step.id}'")

        return errors
