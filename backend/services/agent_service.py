from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models.agent import Agent, AgentExecution
from backend.exceptions import AgentExecutionException, AgentNotFoundException
from backend.repositories.agent_repository import AgentExecutionRepository, AgentRepository


class AgentService:
    """Service layer for Agent business logic."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = AgentRepository(db)
        self.execution_repository = AgentExecutionRepository(db)

    async def get_agent(self, agent_id: str) -> Agent:
        """Get an agent by ID."""
        agent = await self.repository.get_by_id(agent_id)
        if not agent:
            raise AgentNotFoundException()
        return agent

    async def create_agent(
        self,
        project_id: str,
        created_by: str,
        name: str,
        type: str,
        **kwargs: Any,
    ) -> Agent:
        """Create a new agent."""
        valid_types = {"planner", "executor", "reviewer", "tester", "architect", "researcher", "security", "deployment"}
        if type not in valid_types:
            raise AgentExecutionException(detail=f"Invalid agent type: {type}")
        return await self.repository.create(
            project_id=project_id,
            created_by=created_by,
            name=name,
            type=type,
            **kwargs,
        )

    async def update_agent(self, agent_id: str, **kwargs: Any) -> Agent:
        """Update agent fields."""
        await self.get_agent(agent_id)
        updated = await self.repository.update(agent_id, **kwargs)
        if not updated:
            raise AgentNotFoundException()
        return updated

    async def list_agents(
        self,
        project_id: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Agent], int]:
        """List agents, optionally filtered by project."""
        if project_id:
            return await self.repository.get_by_project(project_id, page, page_size)
        return await self.repository.list(page=page, page_size=page_size)

    async def search_agents(
        self,
        query: str,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Agent], int]:
        """Search agents by name or description."""
        return await self.repository.search(query, page=page, page_size=page_size)

    async def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent."""
        await self.get_agent(agent_id)
        return await self.repository.delete(agent_id)

    async def execute_agent(
        self,
        agent_id: str,
        task: str,
        context: dict | None = None,
    ) -> AgentExecution:
        """Start an agent execution."""
        agent = await self.get_agent(agent_id)
        if not agent.is_active:
            raise AgentExecutionException(detail="Agent is not active")

        execution = await self.execution_repository.create(
            agent_id=agent_id,
            task=task,
            context=context or {},
            status="running",
            started_at=datetime.now(timezone.utc),
        )
        return execution

    async def complete_execution(
        self,
        execution_id: str,
        result: dict | None = None,
        error: str | None = None,
        tokens_used: int = 0,
        cost_usd: float = 0.0,
    ) -> AgentExecution:
        """Complete an agent execution with results."""
        execution = await self.execution_repository.get_by_id(execution_id)
        if not execution:
            raise AgentNotFoundException()

        status = "failed" if error else "completed"
        updated = await self.execution_repository.update(
            execution_id,
            status=status,
            result=result,
            error=error,
            tokens_used=tokens_used,
            cost_usd=cost_usd,
            completed_at=datetime.now(timezone.utc),
        )
        if not updated:
            raise AgentExecutionException()
        return updated

    async def list_executions(
        self,
        agent_id: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[AgentExecution], int]:
        """List agent executions, optionally filtered by agent."""
        if agent_id:
            return await self.execution_repository.get_by_agent(agent_id, page, page_size)
        return await self.execution_repository.list(page=page, page_size=page_size)

    async def get_execution_stats(self, agent_id: str | None = None) -> dict[str, Any]:
        """Get execution statistics for an agent or all agents."""
        total_cost = await self.execution_repository.get_total_cost(agent_id)
        total_tokens = await self.execution_repository.get_total_tokens(agent_id)
        running = await self.execution_repository.get_running()
        return {
            "total_cost_usd": total_cost,
            "total_tokens": total_tokens,
            "running_count": len(running),
        }
