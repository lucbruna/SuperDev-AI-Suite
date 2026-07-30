from __future__ import annotations

import time
from typing import Any

from .workflow_definition import WorkflowDefinition


class DefinitionTemplates:
    """Built-in workflow templates."""

    @staticmethod
    def create_default_pipeline(name: str = "pipeline") -> dict[str, Any]:
        return {
            "id": f"pipeline_{int(time.time())}",
            "name": name,
            "version": "1.0.0",
            "description": "Default pipeline workflow",
            "steps": [
                {"id": "init", "name": "Initialize", "action": "init"},
                {"id": "build", "name": "Build", "action": "build", "depends_on": ["init"]},
                {"id": "test", "name": "Test", "action": "test", "depends_on": ["build"]},
                {"id": "deploy", "name": "Deploy", "action": "deploy", "depends_on": ["test"]},
            ],
        }

    @staticmethod
    def create_ci_cd(name: str = "ci_cd") -> dict[str, Any]:
        return {
            "id": f"cicd_{int(time.time())}",
            "name": name,
            "version": "1.0.0",
            "description": "CI/CD pipeline workflow",
            "steps": [
                {"id": "checkout", "name": "Checkout", "action": "git_checkout"},
                {"id": "lint", "name": "Lint", "action": "lint", "depends_on": ["checkout"]},
                {"id": "test", "name": "Test", "action": "test", "depends_on": ["lint"]},
                {"id": "build", "name": "Build", "action": "build", "depends_on": ["test"]},
                {"id": "deploy", "name": "Deploy", "action": "deploy", "depends_on": ["build"]},
            ],
        }
