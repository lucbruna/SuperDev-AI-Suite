"""Intelligence workflow pipeline.

Each workflow is a sequence of steps; the runner executes them and records
outcomes. Workflows are the composable unit behind scheduled refreshes and the
agents() endpoint.
"""
from __future__ import annotations

import time
from typing import Any, Callable


def _step_build(engine: Any, **kwargs: Any) -> dict[str, Any]:
    graph = engine.graph(build_if_missing=True)
    return {"nodes": graph.stats().get("nodes", 0)}


def _step_analyze(engine: Any, **kwargs: Any) -> dict[str, Any]:
    return engine.analyze()


def _step_insights(engine: Any, **kwargs: Any) -> dict[str, Any]:
    insights = engine.insights()
    return {"count": len(insights.get("insights", []))}


def _step_agents(engine: Any, **kwargs: Any) -> dict[str, Any]:
    return engine.agents()


def _step_snapshot(engine: Any, **kwargs: Any) -> dict[str, Any]:
    return engine.snapshot()


STEPS: dict[str, Callable[..., dict[str, Any]]] = {
    "build": _step_build,
    "analyze": _step_analyze,
    "insights": _step_insights,
    "agents": _step_agents,
    "snapshot": _step_snapshot,
}

WORKFLOWS: dict[str, list[str]] = {
    "overview": ["build", "analyze"],
    "insight": ["build", "insights"],
    "agents": ["build", "agents"],
    "monitor": ["build", "analyze", "snapshot"],
}


class WorkflowRunner:
    """Runs a named workflow, collecting per-step results and errors."""

    def __init__(self, engine: Any) -> None:
        self.engine = engine

    def run(self, name: str) -> dict[str, Any]:
        if name not in WORKFLOWS:
            return {"workflow": name, "ok": False, "error": f"unknown workflow: {name}"}
        results: dict[str, Any] = {}
        errors: list[str] = []
        started = time.time()
        for step in WORKFLOWS[name]:
            fn = STEPS.get(step)
            if fn is None:
                errors.append(f"{step}: unknown step")
                continue
            try:
                results[step] = fn(self.engine)
            except Exception as exc:  # pragma: no cover - defensive
                errors.append(f"{step}: {exc}")
        return {
            "workflow": name,
            "ok": not errors,
            "steps": results,
            "errors": errors,
            "duration_seconds": round(time.time() - started, 3),
        }


def run_workflow(engine: Any, name: str) -> dict[str, Any]:
    return WorkflowRunner(engine).run(name)
