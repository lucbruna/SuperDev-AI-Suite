from __future__ import annotations

from typing import Any

from backend.database.models.workflow import Workflow, WorkflowRun
from backend.exceptions import WorkflowNotFoundException, WorkflowValidationException
from backend.repositories.workflow_repository import (
    WorkflowRepository,
    WorkflowRunRepository,
    WorkflowStepRepository,
)
from sqlalchemy.ext.asyncio import AsyncSession


class WorkflowService:
    """Service layer for Workflow business logic."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = WorkflowRepository(db)
        self.run_repository = WorkflowRunRepository(db)
        self.step_repository = WorkflowStepRepository(db)

    async def get_workflow(self, workflow_id: str) -> Workflow:
        """Get a workflow by ID."""
        workflow = await self.repository.get_by_id(workflow_id)
        if not workflow:
            raise WorkflowNotFoundException()
        return workflow

    async def create_workflow(
        self,
        project_id: str,
        created_by: str,
        name: str,
        definition: dict,
        **kwargs: Any,
    ) -> Workflow:
        """Create a new workflow with validation."""
        self._validate_definition(definition)
        return await self.repository.create(
            project_id=project_id,
            created_by=created_by,
            name=name,
            definition=definition,
            **kwargs,
        )

    async def update_workflow(self, workflow_id: str, **kwargs: Any) -> Workflow:
        """Update workflow fields."""
        await self.get_workflow(workflow_id)

        if "definition" in kwargs:
            self._validate_definition(kwargs["definition"])

        # Bump version on definition change
        if "definition" in kwargs:
            workflow = await self.get_workflow(workflow_id)
            kwargs["version"] = workflow.version + 1

        updated = await self.repository.update(workflow_id, **kwargs)
        if not updated:
            raise WorkflowNotFoundException()
        return updated

    async def list_workflows(
        self,
        project_id: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Workflow], int]:
        """List workflows, optionally filtered by project."""
        if project_id:
            return await self.repository.get_by_project(project_id, page, page_size)
        return await self.repository.list(page=page, page_size=page_size)

    async def get_templates(
        self,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Workflow], int]:
        """List workflow templates."""
        return await self.repository.get_templates(page, page_size)

    async def search_workflows(
        self,
        query: str,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Workflow], int]:
        """Search workflows by name or description."""
        return await self.repository.search(query, page=page, page_size=page_size)

    async def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow."""
        await self.get_workflow(workflow_id)
        return await self.repository.delete(workflow_id)

    async def create_run(
        self,
        workflow_id: str,
        trigger: str,
        triggered_by: str | None = None,
        variables: dict | None = None,
    ) -> WorkflowRun:
        """Create a new workflow run."""
        await self.get_workflow(workflow_id)
        return await self.run_repository.create(
            workflow_id=workflow_id,
            trigger=trigger,
            triggered_by=triggered_by,
            variables=variables or {},
        )

    async def get_run(self, run_id: str) -> WorkflowRun:
        """Get a workflow run by ID."""
        run = await self.run_repository.get_by_id(run_id)
        if not run:
            raise WorkflowNotFoundException()
        return run

    async def list_runs(
        self,
        workflow_id: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[WorkflowRun], int]:
        """List workflow runs, optionally filtered by workflow."""
        if workflow_id:
            return await self.run_repository.get_by_workflow(workflow_id, page, page_size)
        return await self.run_repository.list(page=page, page_size=page_size)

    def _validate_definition(self, definition: dict) -> None:
        """Validate a workflow definition structure."""
        if not definition:
            raise WorkflowValidationException("Empty definition")
        if "nodes" not in definition and "steps" not in definition:
            raise WorkflowValidationException("Definition must contain 'nodes' or 'steps'")
