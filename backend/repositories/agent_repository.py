from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models.agent import Agent, AgentExecution
from backend.repositories.base_repository import BaseRepository


class AgentRepository(BaseRepository[Agent]):
    """Repository for Agent entity with domain-specific queries."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, Agent)

    async def get_by_project(
        self,
        project_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Agent], int]:
        """List agents belonging to a project."""
        return await self.list(page=page, page_size=page_size, filters={"project_id": project_id})

    async def get_by_type(
        self,
        agent_type: str,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Agent], int]:
        """List agents of a specific type."""
        return await self.list(page=page, page_size=page_size, filters={"type": agent_type})

    async def get_by_name(self, name: str) -> Agent | None:
        """Get a single agent by exact name (first match)."""
        query = select(self.model).where(self.model.name == name).limit(1)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_active_by_project(self, project_id: str) -> list[Agent]:
        """Get all active agents for a project."""
        query = select(self.model).where(
            self.model.project_id == project_id,
            self.model.is_active,
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def search(
        self,
        query_str: str,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Agent], int]:
        """Search agents by name or description."""
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


class AgentExecutionRepository(BaseRepository[AgentExecution]):
    """Repository for AgentExecution entity with domain-specific queries."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, AgentExecution)

    async def get_by_agent(
        self,
        agent_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[AgentExecution], int]:
        """List executions for a specific agent."""
        return await self.list(page=page, page_size=page_size, filters={"agent_id": agent_id})

    async def get_by_status(
        self,
        status: str,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[AgentExecution], int]:
        """List executions with a specific status."""
        return await self.list(page=page, page_size=page_size, filters={"status": status})

    async def get_by_run(
        self,
        run_id: str,
    ) -> list[AgentExecution]:
        """Get all executions associated with a workflow run."""
        query = select(self.model).where(self.model.run_id == run_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_running(self) -> list[AgentExecution]:
        """Get all currently running agent executions."""
        query = select(self.model).where(self.model.status == "running")
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_total_cost(
        self,
        agent_id: str | None = None,
    ) -> float:
        """Calculate total cost across executions, optionally for a specific agent."""
        query = select(func.sum(self.model.cost_usd))
        if agent_id:
            query = query.where(self.model.agent_id == agent_id)
        result = await self.db.execute(query)
        return float(result.scalar() or 0)

    async def get_total_tokens(
        self,
        agent_id: str | None = None,
    ) -> int:
        """Calculate total tokens used, optionally for a specific agent."""
        query = select(func.sum(self.model.tokens_used))
        if agent_id:
            query = query.where(self.model.agent_id == agent_id)
        result = await self.db.execute(query)
        return int(result.scalar() or 0)
