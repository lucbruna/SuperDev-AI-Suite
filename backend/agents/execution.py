"""Shared DB-backed agent execution flow.

Single source of truth for running a persisted agent (ReActAgent + AgentService
execution lifecycle). Used by the agents API, the system API and the workflow
integration service so every entry point records executions the same way.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.agents.react_agent import ReActAgent
from backend.database.models.agent import Agent
from backend.services.agent_service import AgentService


async def run_persisted_agent(
    db: AsyncSession,
    agent: Agent,
    task: str,
    context: dict | None = None,
) -> dict[str, Any]:
    """Execute a persisted agent via ReActAgent and persist the execution.

    Caller is responsible for resolving the agent and checking ``is_active``.
    """
    service = AgentService(db)
    execution = await service.execute_agent(
        agent_id=str(agent.id),
        task=task,
        context=context,
    )

    config = agent.config or {}
    react_agent = ReActAgent(
        name=agent.name,
        description=agent.description or "",
        model=agent.model_name,
        provider=agent.model_provider,
        max_steps=config.get("max_steps", 10),
        temperature=config.get("temperature", 0.7),
        db=db,
    )
    if agent.tools:
        enabled = set(agent.tools)
        react_agent._tools = [t for t in react_agent._tools if t["name"] in enabled]

    result = await react_agent.run(task, context)

    tokens_used = 0
    if result.token_usage:
        tokens_used = int(result.token_usage.get("total_tokens", 0) or 0)

    await service.complete_execution(
        str(execution.id),
        result={
            "output": result.output,
            "steps": len(result.steps),
            "tool_calls": len(result.tool_calls),
        },
        error=result.error,
        tokens_used=tokens_used,
    )

    return {
        "execution_id": str(execution.id),
        "agent_id": str(agent.id),
        "output": result.output,
        "steps": [
            {"thought": s.thought, "action": s.action, "observation": s.observation}
            for s in result.steps
        ],
        "tool_calls": [
            {"name": tc.name, "arguments": tc.arguments, "result": tc.result, "error": tc.error}
            for tc in result.tool_calls
        ],
        "execution_time_ms": result.execution_time_ms,
        "error": result.error,
        "success": not result.error,
    }
