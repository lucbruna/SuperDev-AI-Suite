from __future__ import annotations

import logging
import time
import uuid
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .cicd_engine import CICDEngine


class PipelineRunner:
    """Runs CI/CD pipelines with stage orchestration."""

    def __init__(self, engine: CICDEngine) -> None:
        self._log = logging.getLogger("superdev.devops.cicd.runner")
        self._engine = engine
        self._runs: dict[str, dict[str, Any]] = {}

    def run(self, pipeline_id: str, **kwargs: Any) -> dict[str, Any]:
        """Run every stage of a pipeline in order. Stops on first failure."""
        pipeline = self._engine.builder.get(pipeline_id)
        run_id = f"run-{uuid.uuid4().hex[:8]}"
        record: dict[str, Any] = {
            "run_id": run_id,
            "pipeline_id": pipeline_id,
            "name": pipeline["name"],
            "status": "running",
            "started_at": time.time(),
            "finished_at": None,
            "stages": [],
            "logs": [],
        }
        self._runs[run_id] = record
        stage_factory = self._engine.stage_factory
        for stage in pipeline["stages"]:
            stage_type = stage.get("type", "build")
            stage_cls = stage_factory.get(stage_type)
            config = dict(stage.get("config", {}))
            config.update(kwargs)
            result = stage_cls().run(config) if stage_cls else {
                "ok": True, "status": "skipped", "error": f"unknown stage type: {stage_type}"
            }
            entry = {
                "name": stage.get("name", stage_type),
                "type": stage_type,
                "status": result.get("status", "unknown"),
            }
            record["stages"].append(entry)
            record["logs"].append(f"[{stage_type}] {entry['status']}")
            if not result.get("ok", True):
                record["status"] = "failed"
                record["finished_at"] = time.time()
                record["error"] = result.get("errors") or result.get("error")
                self._engine._persist()
                return dict(record)
        record["status"] = "passed"
        record["finished_at"] = time.time()
        self._engine._persist()
        return dict(record)

    def cancel(self, pipeline_id: str) -> bool:
        """Cancel all running runs for a pipeline."""
        cancelled = False
        for run in self._runs.values():
            if run["pipeline_id"] == pipeline_id and run["status"] == "running":
                run["status"] = "cancelled"
                run["finished_at"] = time.time()
                cancelled = True
        if cancelled:
            self._engine._persist()
        return cancelled

    def get_logs(self, pipeline_id: str) -> list[str]:
        for run in self._runs.values():
            if run["pipeline_id"] == pipeline_id:
                return list(run["logs"])
        return []

    def get_run(self, run_id: str) -> dict[str, Any]:
        run = self._runs.get(run_id)
        if run is None:
            raise KeyError(f"run not found: {run_id}")
        return dict(run)

    def list_runs(self, pipeline_id: str | None = None) -> list[dict[str, Any]]:
        runs = list(self._runs.values())
        if pipeline_id is not None:
            runs = [r for r in runs if r["pipeline_id"] == pipeline_id]
        return [dict(r) for r in runs]

    # -- persistence ---------------------------------------------------------

    def snapshot_state(self) -> dict[str, Any]:
        """Collect the pipeline run records for JSON persistence."""
        return dict(self._runs)

    def restore_state(self, data: dict[str, Any]) -> None:
        """Restore pipeline run records from persisted JSON (tolerant)."""
        for run_id, record in data.items():
            if isinstance(run_id, str) and isinstance(record, dict):
                self._runs[run_id] = record
