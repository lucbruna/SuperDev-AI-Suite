from __future__ import annotations

from typing import Any

from backend.utils.uuid_utils import generate_uuid
from backend.workflow.base_workflow import (
    StepConfig,
    StepType,
    WorkflowDefinition,
    WorkflowStatus,
)
from backend.workflow.executor import workflow_executor


class WorkflowManager:
    """Manages workflow definitions and execution."""

    def __init__(self):
        self._definitions: dict[str, WorkflowDefinition] = {}
        self._runs: dict[str, dict[str, Any]] = {}
        self._executor = workflow_executor

    def create_definition(
        self,
        name: str,
        steps: list[dict[str, Any]],
        description: str = "",
        variables: dict[str, Any] | None = None,
        tags: list[str] | None = None,
    ) -> WorkflowDefinition:
        workflow_id = generate_uuid()

        step_configs = []
        for step_data in steps:
            step_config = StepConfig(
                id=step_data.get("id", generate_uuid()),
                name=step_data.get("name", "Unnamed Step"),
                step_type=StepType(step_data.get("step_type", "code")),
                config=step_data.get("config", {}),
                depends_on=step_data.get("depends_on", []),
                max_retries=step_data.get("max_retries", 3),
                timeout_seconds=step_data.get("timeout_seconds", 300),
                continue_on_error=step_data.get("continue_on_error", False),
            )
            step_configs.append(step_config)

        definition = WorkflowDefinition(
            id=workflow_id,
            name=name,
            description=description,
            steps=step_configs,
            variables=variables or {},
            tags=tags or [],
        )

        errors = definition.validate()
        if errors:
            raise ValueError(f"Invalid workflow: {'; '.join(errors)}")

        self._definitions[workflow_id] = definition
        return definition

    def get_definition(self, workflow_id: str) -> WorkflowDefinition | None:
        return self._definitions.get(workflow_id)

    def list_definitions(self, tags: list[str] | None = None) -> list[WorkflowDefinition]:
        definitions = list(self._definitions.values())
        if tags:
            definitions = [d for d in definitions if any(t in d.tags for t in tags)]
        return definitions

    def delete_definition(self, workflow_id: str) -> bool:
        if workflow_id in self._definitions:
            del self._definitions[workflow_id]
            return True
        return False

    async def execute_workflow(
        self,
        workflow_id: str,
        variables: dict[str, Any] | None = None,
        user_id: str | None = None,
    ) -> dict[str, Any]:
        definition = self._definitions.get(workflow_id)
        if not definition:
            return {
                "run_id": "",
                "status": "failed",
                "error": f"Workflow not found: {workflow_id}",
            }

        run_id = generate_uuid()
        self._runs[run_id] = {
            "workflow_id": workflow_id,
            "status": WorkflowStatus.RUNNING.value,
            "user_id": user_id,
        }

        result = await self._executor.execute(definition, run_id, variables, user_id)
        self._runs[run_id]["status"] = result.get("status", "failed")

        return result

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        return self._runs.get(run_id)

    def list_runs(self, workflow_id: str | None = None) -> list[dict[str, Any]]:
        runs = list(self._runs.values())
        if workflow_id:
            runs = [r for r in runs if r.get("workflow_id") == workflow_id]
        return runs

    async def cancel_run(self, run_id: str) -> bool:
        return await self._executor.cancel(run_id)


workflow_manager = WorkflowManager()


BUILTIN_WORKFLOWS = [
    {
        "name": "code_review_pipeline",
        "description": "Automated code review pipeline",
        "steps": [
            {
                "id": "lint",
                "name": "Run Linter",
                "step_type": "code",
                "config": {
                    "language": "python",
                    "code": "print('Linting passed')",
                },
            },
            {
                "id": "test",
                "name": "Run Tests",
                "step_type": "code",
                "config": {
                    "language": "python",
                    "code": "print('Tests passed')",
                },
                "depends_on": ["lint"],
            },
            {
                "id": "review",
                "name": "AI Code Review",
                "step_type": "code",
                "config": {
                    "language": "python",
                    "code": "print('Code review completed')",
                },
                "depends_on": ["test"],
            },
        ],
        "tags": ["code", "review", "ci"],
    },
    {
        "name": "deploy_pipeline",
        "description": "Application deployment pipeline",
        "steps": [
            {
                "id": "build",
                "name": "Build Application",
                "step_type": "code",
                "config": {
                    "language": "shell",
                    "code": "echo 'Building application...'",
                },
            },
            {
                "id": "test",
                "name": "Run Tests",
                "step_type": "code",
                "config": {
                    "language": "shell",
                    "code": "echo 'Running tests...'",
                },
                "depends_on": ["build"],
            },
            {
                "id": "deploy",
                "name": "Deploy to Production",
                "step_type": "code",
                "config": {
                    "language": "shell",
                    "code": "echo 'Deploying...'",
                },
                "depends_on": ["test"],
            },
        ],
        "tags": ["deploy", "ci", "cd"],
    },
]


for wf_data in BUILTIN_WORKFLOWS:
    try:
        workflow_manager.create_definition(**wf_data)
    except Exception:
        pass
