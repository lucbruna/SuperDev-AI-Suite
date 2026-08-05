"""WorkflowEngine: executes workflow definitions deterministically in DAG order."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from aios.workflows.workflow_dag import WorkflowDAG
from aios.workflows.workflow_definitions import NodeFunc, WorkflowDefinition
from aios.workflows.workflow_state import WorkflowState

#: monitor hook: (WorkflowEngine, WorkflowRunResult) -> None
MonitorHook = Callable[["WorkflowEngine", "WorkflowRunResult"], None]


@dataclass
class WorkflowRunResult:
    workflow_id: str
    ok: bool
    order: list[str] = field(default_factory=list)
    executed: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)
    statuses: dict[str, str] = field(default_factory=dict)
    results: dict[str, Any] = field(default_factory=dict)
    errors: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "ok": self.ok,
            "order": list(self.order),
            "executed": list(self.executed),
            "skipped": list(self.skipped),
            "failed": list(self.failed),
            "statuses": dict(self.statuses),
            "results": dict(self.results),
            "errors": dict(self.errors),
        }


class WorkflowEngine:
    """Runs a definition in topological order, honouring edge conditions.

    A node runs only when every incoming edge's condition (if any) returns
    True and no upstream node failed. A failed node marks its downstream
    nodes as skipped.
    """

    def __init__(
        self,
        functions: dict[str, NodeFunc] | None = None,
        monitor: Optional[MonitorHook] = None,
    ) -> None:
        self.functions: dict[str, NodeFunc] = dict(functions or {})
        self.monitor = monitor

    def register(self, node_id: str, func: NodeFunc) -> None:
        self.functions[node_id] = func

    def run(
        self,
        definition: WorkflowDefinition,
        functions: dict[str, NodeFunc] | None = None,
        context: dict[str, Any] | None = None,
    ) -> WorkflowRunResult:
        functions = {**self.functions, **(functions or {})}
        dag = WorkflowDAG(definition)
        problems = dag.validate()
        if problems:
            raise ValueError(f"invalid workflow: {problems}")
        order = dag.topological_order()
        state = WorkflowState(order)
        ctx: dict[str, Any] = dict(context or {})

        for node_id in order:
            node = dag.nodes[node_id]
            if node_id not in functions:
                state.fail(node_id, f"no function registered for node {node_id!r}")
                continue
            incoming = sorted(dag.edges_to(node_id), key=lambda e: e.source)
            blocked = False
            for edge in incoming:
                source_status = state.status(edge.source)
                if source_status == "failed":
                    blocked = True
                    break
                if source_status != "succeeded":
                    blocked = True
                    break
                if edge.condition is not None:
                    if not edge.condition(ctx, state.result(edge.source)):
                        blocked = True
                        break
            if blocked:
                state.mark(node_id, "skipped")
                continue
            state.mark(node_id, "running")
            try:
                result = functions[node_id](ctx, node)
                state.store(node_id, result)
                ctx[node_id] = result
            except Exception as exc:  # noqa: BLE001 - any node failure is a run failure
                state.fail(node_id, str(exc))

        failed = sorted(node_id for node_id, status in state.snapshot()["statuses"].items()
                        if status == "failed")
        result = WorkflowRunResult(
            workflow_id=definition.workflow_id,
            ok=not failed,
            order=order,
            executed=state.executed(),
            skipped=sorted(
                node_id for node_id, status in state.snapshot()["statuses"].items()
                if status == "skipped"
            ),
            failed=failed,
            statuses=dict(state.snapshot()["statuses"]),
            results=state.results(),
            errors=state.errors(),
        )
        if self.monitor is not None:
            self.monitor(self, result)
        return result
