from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models.workflow import Workflow, WorkflowRun, WorkflowStep
from backend.repositories.base_repository import BaseRepository


class WorkflowRepository(BaseRepository[Workflow]):
    """Repository for Workflow entity with domain-specific queries."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, Workflow)

    async def get_by_project(
        self,
        project_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Workflow], int]:
        """List workflows belonging to a project."""
        return await self.list(page=page, page_size=page_size, filters={"project_id": project_id})

    async def get_templates(
        self,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Workflow], int]:
        """List workflow templates."""
        return await self.list(page=page, page_size=page_size, filters={"is_template": True})

    async def search(
        self,
        query_str: str,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Workflow], int]:
        """Search workflows by name or description."""
        pattern = f"%{query_str}%"
        where_clause = (self.model.name.ilike(pattern)) | (self.model.description.ilike(pattern))

        query = select(self.model).where(where_clause)
        count_query = select(func.count()).select_from(self.model).where(where_clause)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def get_by_creator(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Workflow], int]:
        """List workflows created by a specific user."""
        return await self.list(page=page, page_size=page_size, filters={"created_by": user_id})


class WorkflowRunRepository(BaseRepository[WorkflowRun]):
    """Repository for WorkflowRun entity with domain-specific queries."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, WorkflowRun)

    async def get_by_workflow(
        self,
        workflow_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[WorkflowRun], int]:
        """List runs for a specific workflow."""
        return await self.list(page=page, page_size=page_size, filters={"workflow_id": workflow_id})

    async def get_by_status(
        self,
        status: str,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[WorkflowRun], int]:
        """List runs with a specific status."""
        return await self.list(page=page, page_size=page_size, filters={"status": status})

    async def get_by_trigger_user(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[WorkflowRun], int]:
        """List runs triggered by a specific user."""
        return await self.list(page=page, page_size=page_size, filters={"triggered_by": user_id})

    async def get_running(self) -> list[WorkflowRun]:
        """Get all currently running workflow executions."""
        query = select(self.model).where(self.model.status == "running")
        result = await self.db.execute(query)
        return list(result.scalars().all())


class WorkflowStepRepository(BaseRepository[WorkflowStep]):
    """Repository for WorkflowStep entity with domain-specific queries."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, WorkflowStep)

    async def get_by_run(self, run_id: str) -> list[WorkflowStep]:
        """Get all steps for a specific workflow run, ordered by creation."""
        query = select(self.model).where(self.model.run_id == run_id).order_by(self.model.created_at)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_status(
        self,
        status: str,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[WorkflowStep], int]:
        """List steps with a specific status."""
        return await self.list(page=page, page_size=page_size, filters={"status": status})
