"""WorkflowMonitor: aggregates run results into per-workflow stats and failures."""
from __future__ import annotations

from typing import Any

from aios.workflows.workflow_engine import WorkflowRunResult


class WorkflowMonitor:
    """Records completed runs and exposes deterministic aggregate metrics."""

    def __init__(self) -> None:
        self._runs: list[WorkflowRunResult] = []

    def record(self, result: WorkflowRunResult) -> None:
        self._runs.append(result)

    def runs(self) -> list[WorkflowRunResult]:
        return list(self._runs)

    def run_stats(self, workflow_id: str) -> dict[str, Any]:
        runs = [run for run in self._runs if run.workflow_id == workflow_id]
        if not runs:
            return {
                "workflow_id": workflow_id,
                "runs": 0,
                "ok": 0,
                "failed": 0,
                "avg_nodes_executed": 0.0,
            }
        ok = sum(1 for run in runs if run.ok)
        avg_nodes = sum(len(run.executed) for run in runs) / len(runs)
        return {
            "workflow_id": workflow_id,
            "runs": len(runs),
            "ok": ok,
            "failed": len(runs) - ok,
            "avg_nodes_executed": round(avg_nodes, 2),
        }

    def failures(self) -> list[dict[str, Any]]:
        return [
            {
                "workflow_id": run.workflow_id,
                "failed_nodes": list(run.failed),
                "errors": dict(run.errors),
            }
            for run in self._runs
            if not run.ok
        ]

    def total_runs(self) -> int:
        return len(self._runs)

    def overall_success_rate(self) -> float:
        if not self._runs:
            return 0.0
        return sum(1 for run in self._runs if run.ok) / len(self._runs)

    def snapshot(self) -> dict[str, Any]:
        workflow_ids = sorted({run.workflow_id for run in self._runs})
        return {
            "total_runs": self.total_runs(),
            "success_rate": self.overall_success_rate(),
            "workflows": [self.run_stats(workflow_id) for workflow_id in workflow_ids],
            "failures": self.failures(),
        }
