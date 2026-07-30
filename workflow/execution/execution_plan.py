from __future__ import annotations

from typing import Any


class ExecutionPlan:
    """Ordered execution plan derived from a workflow definition."""

    def __init__(self, steps: list[dict[str, Any]] | None = None) -> None:
        self._steps = steps or []

    @property
    def steps(self) -> list[dict[str, Any]]:
        return list(self._steps)

    def add_step(self, step: dict[str, Any]) -> None:
        self._steps.append(step)

    def get_step(self, step_id: str) -> dict[str, Any] | None:
        for s in self._steps:
            if s.get("id") == step_id:
                return s
        return None

    def next_ready(self, completed: set[str]) -> list[dict[str, Any]]:
        ready: list[dict[str, Any]] = []
        for s in self._steps:
            sid = s["id"]
            if sid in completed:
                continue
            deps = set(s.get("depends_on", []))
            if deps.issubset(completed):
                ready.append(s)
        return ready

    def __len__(self) -> int:
        return len(self._steps)
