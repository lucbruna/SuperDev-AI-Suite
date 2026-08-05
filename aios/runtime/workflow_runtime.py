"""AIOS Workflow Runtime — executes workflow step graphs.

A workflow spec is a list of steps ``{"id", "run", "depends_on": []}``.
The runtime resolves the topological order locally and executes steps,
recording per-step outcomes. Self-contained (no cross-package import)
so the runtime package is importable on its own.
"""

from __future__ import annotations

import inspect
from typing import Any, Awaitable, Callable

from .runtime import BaseRuntime, RuntimeCallable

StepRunner = Callable[[str, dict[str, Any]], Awaitable[dict[str, Any]] | dict[str, Any]]


def _topological_sort(steps: list[dict[str, Any]]) -> tuple[list[str], list[str]]:
    """Return (order, cycle). Deterministic Kahn's algorithm."""
    nodes = {step["id"] for step in steps}
    edges: dict[str, set[str]] = {node: set() for node in nodes}
    reverse: dict[str, set[str]] = {node: set() for node in nodes}
    for step in steps:
        for dep in step.get("depends_on", []):
            if dep in nodes:
                edges[dep].add(step["id"])
                reverse[step["id"]].add(dep)
    ready = sorted(n for n in nodes if not reverse[n])
    order: list[str] = []
    while ready:
        node = ready.pop(0)
        order.append(node)
        for successor in sorted(edges[node]):
            reverse[successor].discard(node)
            if not reverse[successor]:
                ready.append(successor)
                ready.sort()
    cycle = [n for n in nodes if reverse[n]]
    return order, sorted(cycle)


class WorkflowRuntime(BaseRuntime):
    """Execute workflow specs in dependency order."""

    kind = "workflow"

    def __init__(self, name: str = "workflow-runtime") -> None:
        super().__init__(name)

    async def run(self, target: RuntimeCallable, context: dict[str, Any]) -> dict[str, Any]:
        # ``target`` may be a factory returning the spec, or the spec itself.
        spec = target(context) if callable(target) else target
        if not isinstance(spec, dict) or "steps" not in spec:
            return {"ok": False, "error": "workflow spec must be a dict with 'steps'", "results": {}}
        steps: list[dict[str, Any]] = spec["steps"]
        order, cycle = _topological_sort(steps)
        if cycle:
            return {"ok": False, "error": f"cycle detected: {cycle}", "results": {}}
        results: dict[str, Any] = {}
        by_id = {step["id"]: step for step in steps}
        for step_id in order:
            step = by_id[step_id]
            runner: StepRunner = step["run"]
            inputs = dict(context.get("inputs", {}))
            for dep in step.get("depends_on", []):
                inputs.update(results.get(dep, {}))
            outcome = runner(step_id, inputs)
            if inspect.isawaitable(outcome):
                outcome = await outcome
            results[step_id] = outcome if isinstance(outcome, dict) else {"value": outcome}
        return {"ok": True, "results": results, "order": order}
