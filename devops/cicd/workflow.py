from __future__ import annotations

import logging
from typing import Any


class CICDWorkflow:
    """Represents a complete CI/CD workflow with all stages."""

    def __init__(self, name: str) -> None:
        self._log = logging.getLogger("superdev.devops.cicd.workflow")
        self.name = name
        self.stages: list[dict[str, Any]] = []

    def add_stage(self, stage: dict[str, Any]) -> None:
        self.stages.append(stage)

    def remove_stage(self, stage_name: str) -> None:
        self.stages = [s for s in self.stages if s.get("name") != stage_name]

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "stages": self.stages}

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.name:
            errors.append("Workflow name is required")
        if not self.stages:
            errors.append("Workflow must have at least one stage")
        return errors
