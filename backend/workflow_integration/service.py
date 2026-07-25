from __future__ import annotations

import asyncio
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.session import get_db
from backend.workflow.workflow_manager import workflow_manager
from backend.workflow.base_workflow import StepConfig, StepType, WorkflowDefinition, WorkflowStatus
from backend.workflow.executor import workflow_executor
from backend.ai_platform.providers.provider_registry import ProviderRegistry
from backend.verification.verification_loop import VerificationLoop
from backend.verification.models import VerificationResult, VerificationStage


class WorkflowIntegrationService:
    def __init__(self):
        self.provider_registry = ProviderRegistry()
        self._running_workflows: dict[UUID, asyncio.Task] = {}

    async def create_and_execute_workflow(
        self,
        name: str,
        description: str,
        steps: list[dict[str, Any]],
        variables: dict[str, Any] | None = None,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        definition = workflow_manager.create_definition(
            name=name,
            description=description,
            steps=steps,
            variables=variables or {},
            tags=tags or [],
        )

        run_id = uuid4()
        result = await workflow_executor.execute(
            definition=definition,
            run_id=run_id,
            variables=variables or {},
        )

        return {
            "workflow_id": str(definition.id),
            "run_id": str(run_id),
            "status": result.get("status"),
            "result": result,
        }

    async def run_verification_workflow(
        self,
        task_description: str,
        language: str = "python",
        context: str | None = None,
        requirements: list[str] | None = None,
        existing_code: str | None = None,
        test_files: dict[str, str] | None = None,
        max_iterations: int = 3,
        provider_name: str | None = None,
    ) -> VerificationResult:
        provider = None
        if provider_name:
            provider_class = self.provider_registry.get(provider_name)
            if provider_class:
                provider = provider_class()

        loop = VerificationLoop(
            provider=provider,
            max_iterations=max_iterations,
        )

        return await loop.run(
            task_description=task_description,
            language=language,
            context=context,
            requirements=requirements,
            existing_code=existing_code,
            test_files=test_files,
        )

    async def create_verification_workflow(
        self,
        name: str,
        task_description: str,
        language: str = "python",
        context: str | None = None,
        requirements: list[str] | None = None,
        existing_code: str | None = None,
        test_files: dict[str, str] | None = None,
        max_iterations: int = 3,
        provider_name: str | None = None,
    ) -> WorkflowDefinition:
        steps = [
            StepConfig(
                id="generate",
                name="Generate Code",
                step_type=StepType.CODE,
                config={
                    "language": language,
                    "code": f"""
# This step is a placeholder - actual generation happens via VerificationLoop
task_description = {task_description!r}
language = {language!r}
""",
                },
            ),
            StepConfig(
                id="execute",
                name="Execute Code",
                step_type=StepType.CODE,
                config={
                    "language": language,
                    "code": "# Code execution will be handled by VerificationLoop",
                },
                depends_on=["generate"],
            ),
            StepConfig(
                id="test",
                name="Run Tests",
                step_type=StepType.CODE,
                config={
                    "language": language,
                    "code": "# Test execution will be handled by VerificationLoop",
                },
                depends_on=["execute"],
            ),
            StepConfig(
                id="review",
                name="Review Code",
                step_type=StepType.CODE,
                config={
                    "language": language,
                    "code": "# Code review will be handled by VerificationLoop",
                },
                depends_on=["test"],
            ),
            StepConfig(
                id="correct",
                name="Correct Code",
                step_type=StepType.CODE,
                config={
                    "language": language,
                    "code": "# Code correction will be handled by VerificationLoop",
                },
                depends_on=["review"],
            ),
        ]

        return workflow_manager.create_definition(
            name=name,
            description=f"Verification workflow for: {task_description[:100]}",
            steps=[s.model_dump() for s in steps],
            variables={
                "task_description": task_description,
                "language": language,
                "context": context,
                "requirements": requirements or [],
                "existing_code": existing_code,
                "test_files": test_files or {},
                "max_iterations": max_iterations,
                "provider_name": provider_name,
            },
            tags=["verification", language],
        )

    async def execute_verification_workflow(
        self,
        workflow_id: str,
        variables: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        definition = workflow_manager.get_definition(workflow_id)
        if not definition:
            raise ValueError(f"Workflow {workflow_id} not found")

        run_id = uuid4()
        merged_variables = {**(definition.variables or {}), **(variables or {})}
        
        result = await workflow_executor.execute(
            definition=definition,
            run_id=run_id,
            variables=merged_variables,
        )

        return result

    def get_workflow_status(self, run_id: str) -> dict[str, Any] | None:
        run = workflow_manager.get_run(run_id)
        if not run:
            return None
        return run

    def list_workflows(self, tags: list[str] | None = None) -> list[WorkflowDefinition]:
        return workflow_manager.list_definitions(tags)

    async def run_agent_task(
        self,
        agent_name: str,
        task: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        from agents.core.agent_system import AgentSystem
        
        system = AgentSystem()
        await system.initialize({})
        
        result = await system.execute_task(agent_name, task, context)
        
        await system.shutdown()
        
        return {
            "success": result.success,
            "output": result.output,
            "error": result.error,
        }


async def get_workflow_integration_service() -> WorkflowIntegrationService:
    return WorkflowIntegrationService()