from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from ..devops_store import load_json, save_json
from .approval_stage import ApprovalStage
from .artifact_stage import ArtifactStage
from .build import BuildStage
from .deploy_stage import DeployStage
from .pipeline_builder import PipelineBuilder
from .pipeline_runner import PipelineRunner
from .security_stage import SecurityStage
from .test_stage import TestStage


class CICDEngine:
    """Continuous Integration / Continuous Delivery engine (in-memory)."""

    def __init__(self, store_path: str | Path | None = None) -> None:
        self._log = logging.getLogger("superdev.devops.cicd")
        self._store = Path(store_path) if store_path else None
        self.builder = PipelineBuilder(self)
        self.runner = PipelineRunner(self)
        # Stage type registry — every stage is instantiable on demand.
        self.stage_factory: dict[str, type] = {
            "build": BuildStage,
            "test": TestStage,
            "security": SecurityStage,
            "deploy": DeployStage,
            "approval": ApprovalStage,
            "artifact": ArtifactStage,
        }
        self._load_state()

    def run_pipeline(self, pipeline: str, **kwargs: Any) -> dict[str, Any]:
        """Run a pipeline by name (finds the newest matching pipeline)."""
        pipelines = [p for p in self.builder.list() if p["name"] == pipeline]
        if not pipelines:
            raise KeyError(f"pipeline not found: {pipeline}")
        return self.runner.run(pipelines[-1]["pipeline_id"], **kwargs)

    def get_status(self, pipeline_id: str) -> dict[str, Any]:
        runs = self.runner.list_runs(pipeline_id)
        return {
            "pipeline_id": pipeline_id,
            "runs": runs,
            "last_status": runs[-1]["status"] if runs else None,
            "last_run_id": runs[-1]["run_id"] if runs else None,
        }

    def list_pipelines(self) -> list[dict[str, Any]]:
        return self.builder.list()

    def status(self) -> dict[str, Any]:
        return {
            "pipelines": len(self.builder.list()),
            "runs": len(self.runner.list_runs()),
        }

    # -- persistence ---------------------------------------------------------

    def _load_state(self) -> None:
        """Restore pipeline definitions and runs from ``cicd.json``."""
        if self._store is None:
            return
        data = load_json(self._store / "cicd.json", default={})
        if not isinstance(data, dict):
            return
        pipelines = data.get("pipelines")
        if isinstance(pipelines, dict):
            self.builder.restore_state(pipelines)
        runs = data.get("runs")
        if isinstance(runs, dict):
            self.runner.restore_state(runs)

    def _persist(self) -> None:
        """Atomically write pipeline definitions + runs to ``cicd.json``."""
        if self._store is None:
            return
        save_json(
            self._store / "cicd.json",
            {
                "pipelines": self.builder.snapshot_state(),
                "runs": self.runner.snapshot_state(),
            },
        )

    def save_state(self) -> None:
        """Persist the cicd state (no-op without ``store_path``)."""
        self._persist()

    def reload_state(self) -> None:
        """Reload the cicd state from disk."""
        self._load_state()
