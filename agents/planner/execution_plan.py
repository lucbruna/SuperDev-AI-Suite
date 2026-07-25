from __future__ import annotations

from typing import Any, Optional

from .planner import Step


class ExecutionPlan:
    def __init__(self) -> None:
        self._steps: list[Step] = []
        self._dependencies: dict[str, list[str]] = {}
        self._completed: set[str] = set()
        self._failed: set[str] = set()

    def load_steps(self, steps: list[Step]) -> None:
        self._steps = steps
        self._dependencies = {}
        for step in steps:
            self._dependencies[step.id] = list(step.depends_on)

    def validate(self) -> bool:
        step_ids = {s.id for s in self._steps}
        for step_id, deps in self._dependencies.items():
            for dep_id in deps:
                if dep_id not in step_ids:
                    return False
        return True

    def get_next_steps(self) -> list[Step]:
        ready = []
        for step in self._steps:
            if step.id in self._completed or step.id in self._failed:
                continue
            deps = self._dependencies.get(step.id, [])
            if all(d in self._completed for d in deps):
                ready.append(step)
        return ready

    def mark_complete(self, step_id: str) -> None:
        self._completed.add(step_id)
        for step in self._steps:
            if step.id == step_id:
                step.status = "completed"
                break

    def mark_failed(self, step_id: str) -> None:
        self._failed.add(step_id)
        for step in self._steps:
            if step.id == step_id:
                step.status = "failed"
                break

    def is_complete(self) -> bool:
        return len(self._completed) == len(self._steps)

    def progress(self) -> dict[str, Any]:
        return {
            "total": len(self._steps),
            "completed": len(self._completed),
            "failed": len(self._failed),
            "pending": len(self._steps) - len(self._completed) - len(self._failed),
        }
