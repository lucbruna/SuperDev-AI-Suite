"""WorkflowExecutor: facade over the engine with run history and snapshots."""
from __future__ import annotations

from typing import Any, Optional

from aios.workflows.workflow_definitions import NodeFunc, WorkflowDefinition
from aios.workflows.workflow_engine import WorkflowEngine, WorkflowRunResult


class WorkflowExecutor:
    """Executes workflows and keeps a deterministic run history."""

    def __init__(self, engine: WorkflowEngine | None = None) -> None:
        self.engine = engine if engine is not None else WorkflowEngine()
        self._history: list[WorkflowRunResult] = []

    def register(self, node_id: str, func: NodeFunc) -> None:
        self.engine.register(node_id, func)

    def execute(
        self,
        definition: WorkflowDefinition,
        functions: dict[str, NodeFunc] | None = None,
        context: dict[str, Any] | None = None,
    ) -> WorkflowRunResult:
        result = self.engine.run(definition, functions=functions, context=context)
        self._history.append(result)
        return result

    def history(self) -> list[WorkflowRunResult]:
        return list(self._history)

    def last_run(self) -> Optional[WorkflowRunResult]:
        return self._history[-1] if self._history else None

    def run_count(self) -> int:
        return len(self._history)

    def success_rate(self) -> float:
        if not self._history:
            return 0.0
        return sum(1 for run in self._history if run.ok) / len(self._history)

    def snapshot(self) -> dict[str, Any]:
        last = self.last_run()
        return {
            "runs": self.run_count(),
            "success_rate": self.success_rate(),
            "last": last.to_dict() if last is not None else None,
        }
