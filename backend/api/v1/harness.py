"""Ultra Harness API - exposes harness capabilities via REST API."""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(tags=["harness"])


class TaskRequest(BaseModel):
    """Request to execute a task through the harness."""

    description: str
    domain: str | None = None
    required_capabilities: list[str] = []
    priority: int = 5
    timeout_seconds: int = 600
    context: dict[str, Any] = {}


class TaskResponse(BaseModel):
    """Response from a harness task execution."""

    task_id: str
    success: bool
    output: str
    agent_used: str | None = None
    skills_used: list[str] = []
    domain: str | None = None
    duration_ms: float = 0.0
    metrics: dict[str, Any] = {}
    error: str | None = None


# Lazy-loaded harness instance
_harness = None


def _get_harness():
    global _harness
    if _harness is None:
        from harness.orchestrator import UltraHarness
        _harness = UltraHarness()
    return _harness


@router.get("/status")
async def get_status() -> dict[str, Any]:
    """Get harness status and configuration."""
    harness = _get_harness()
    return harness.get_status()


@router.get("/domains")
async def list_domains() -> dict[str, Any]:
    """List all agent domains and their configurations."""
    harness = _get_harness()
    config = harness.get_config()
    return config.to_dict()


@router.get("/agents")
async def list_agents() -> dict[str, Any]:
    """List all registered agent profiles."""
    harness = _get_harness()
    profiles = harness.get_profiles()
    return profiles.to_dict()


@router.get("/skills")
async def list_skills() -> dict[str, Any]:
    """List all registered skills."""
    harness = _get_harness()
    skills = harness.get_skills()
    return skills.to_dict()


@router.get("/skills/{skill_id}")
async def get_skill(skill_id: str) -> dict[str, Any]:
    """Get a specific skill's details and content."""
    harness = _get_harness()
    skills = harness.get_skills()
    skill = skills.get(skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail=f"Skill not found: {skill_id}")

    content = skills.get_skill_content(skill_id)
    return {
        "skill_id": skill.skill_id,
        "name": skill.name,
        "domain": skill.domain.value,
        "description": skill.description,
        "tags": skill.tags,
        "content": content,
    }


@router.post("/execute", response_model=TaskResponse)
async def execute_task(request: TaskRequest) -> TaskResponse:
    """Execute a task through the harness, auto-selecting the best agent and skills."""
    harness = _get_harness()

    from harness.orchestrator import TaskRequest as HarnessTaskRequest
    from harness.config import AgentDomain

    domain = None
    if request.domain:
        try:
            domain = AgentDomain(request.domain)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid domain: {request.domain}. Valid: {[d.value for d in AgentDomain]}",
            )

    task_request = HarnessTaskRequest(
        task_id=str(uuid.uuid4()),
        description=request.description,
        domain=domain,
        required_capabilities=request.required_capabilities,
        priority=request.priority,
        timeout_seconds=request.timeout_seconds,
        context=request.context,
    )

    result = await harness.execute_task(task_request)

    return TaskResponse(
        task_id=result.task_id,
        success=result.success,
        output=result.output,
        agent_used=result.agent_used,
        skills_used=result.skills_used,
        domain=result.domain,
        duration_ms=result.duration_ms,
        metrics=result.metrics,
        error=result.error,
    )


@router.get("/history")
async def get_history() -> list[dict[str, Any]]:
    """Get task execution history."""
    harness = _get_harness()
    return harness.get_task_history()
