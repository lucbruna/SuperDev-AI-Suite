from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import text as sa_text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.agents.react_agent import ReActAgent
from backend.agents.tool_registry import tool_registry
from backend.auth.rbac import Action, Resource, require_permission
from backend.database.session import get_db
from backend.dependencies import get_current_active_user
from backend.exceptions import AgentExecutionException, AgentNotFoundException
from backend.services.agent_service import AgentService
from backend.utils.uuid_utils import generate_uuid

router = APIRouter(dependencies=[Depends(get_current_active_user)])


# ── Request / Response Models ────────────────────────────────────────────────


class AgentCreateRequest(BaseModel):
    name: str
    description: str = ""
    agent_type: str = "react"
    model: str | None = None
    provider: str | None = None
    max_steps: int = 10
    temperature: float = 0.7
    system_prompt: str | None = None
    tools_enabled: list[str] | None = None
    template_id: str | None = None


class AgentUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    model: str | None = None
    provider: str | None = None
    max_steps: int | None = None
    temperature: float | None = None
    system_prompt: str | None = None
    tools_enabled: list[str] | None = None


class AgentExecuteRequest(BaseModel):
    input: str
    context: dict | None = None


class AgentResponse(BaseModel):
    id: str
    name: str
    description: str
    agent_type: str
    status: str
    tools: list[dict]
    model: str | None = None
    provider: str | None = None
    max_steps: int = 10
    temperature: float = 0.7
    system_prompt: str | None = None
    template_id: str | None = None


class AgentTemplateResponse(BaseModel):
    id: str
    name: str
    description: str
    agent_type: str
    model: str
    provider: str
    max_steps: int
    temperature: float
    system_prompt: str
    tools_enabled: list[str]
    category: str
    icon: str


class AgentExecuteResponse(BaseModel):
    execution_id: str
    agent_id: str
    output: str
    steps: list[dict]
    tool_calls: list[dict]
    execution_time_ms: float
    error: str | None = None


# ── Type / Schema Helpers ────────────────────────────────────────────────────

# The DB Agent.type column is a fixed enum that does not include "react".
# Map every supported API agent_type to the closest valid DB enum value and
# preserve the original agent_type in the agent's config JSONB so the
# response contract stays unchanged.
AGENT_TYPE_TO_DB_TYPE = {
    "react": "executor",
    "planner_executor": "planner",
    "code": "executor",
    "review": "reviewer",
    "chat": "executor",
}


def _db_type_for(agent_type: str) -> str:
    return AGENT_TYPE_TO_DB_TYPE.get(agent_type, "executor")


def _tool_schemas(enabled: list[str] | None) -> list[dict[str, Any]]:
    """Return full tool schemas for the enabled tool names (all if unset)."""
    schemas = tool_registry.get_schemas()
    if not enabled:
        return schemas
    by_name = {s["name"]: s for s in schemas}
    return [by_name[n] for n in enabled if n in by_name]


def _agent_response(agent: Any) -> AgentResponse:
    config = agent.config or {}
    return AgentResponse(
        id=str(agent.id),
        name=agent.name,
        description=agent.description or "",
        agent_type=config.get("agent_type", "react"),
        status="running" if agent.is_active else "idle",
        tools=_tool_schemas(agent.tools),
        model=agent.model_name,
        provider=agent.model_provider,
        max_steps=config.get("max_steps", 10),
        temperature=config.get("temperature", 0.7),
        system_prompt=agent.system_prompt,
        template_id=config.get("template_id"),
    )


async def _resolve_project_id(db: AsyncSession, user_id: str) -> str:
    """Resolve the project an agent belongs to, creating a personal one if needed."""
    row = await db.execute(
        sa_text("SELECT id FROM projects WHERE owner_id = :uid ORDER BY created_at LIMIT 1"),
        {"uid": user_id},
    )
    proj = row.fetchone()
    if proj:
        return str(proj[0])

    row = await db.execute(
        sa_text("SELECT project_id FROM project_members WHERE user_id = :uid LIMIT 1"),
        {"uid": user_id},
    )
    proj = row.fetchone()
    if proj:
        return str(proj[0])

    # No project yet — create a personal workspace.
    org_result = await db.execute(
        sa_text("SELECT organization_id FROM organization_members WHERE user_id = :uid LIMIT 1"),
        {"uid": user_id},
    )
    org_row = org_result.fetchone()
    if org_row is None:
        org_result = await db.execute(sa_text("SELECT id FROM organizations LIMIT 1"))
        org_row = org_result.fetchone()
    if org_row is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No organization available to create a project",
        )

    pid = generate_uuid()
    await db.execute(
        sa_text(
            """INSERT INTO projects (id, organization_id, owner_id, name, slug, description)
               VALUES (:id, :organization_id, :owner_id, :name, :slug, :desc)"""
        ),
        {
            "id": pid,
            "organization_id": str(org_row[0]),
            "owner_id": user_id,
            "name": "Personal",
            "slug": f"personal-{user_id[:8]}",
            "desc": "Personal workspace for agents",
        },
    )
    await db.commit()
    return pid


# ── Agent Templates ──────────────────────────────────────────────────────────

AGENT_TEMPLATES: list[dict[str, Any]] = [
    {
        "id": "code-reviewer",
        "name": "Code Reviewer",
        "description": "Reviews code for bugs, security issues, and style problems",
        "agent_type": "react",
        "model": "gpt-4",
        "provider": "openai",
        "max_steps": 15,
        "temperature": 0.3,
        "system_prompt": "You are an expert code reviewer. Analyze code for bugs, security vulnerabilities, performance issues, and style problems. Provide actionable feedback.",
        "tools_enabled": ["file_read", "grep", "glob"],
        "category": "Development",
        "icon": "🔍",
    },
    {
        "id": "debugger",
        "name": "Debug Assistant",
        "description": "Helps diagnose and fix bugs systematically",
        "agent_type": "react",
        "model": "gpt-4",
        "provider": "openai",
        "max_steps": 20,
        "temperature": 0.3,
        "system_prompt": "You are a debugging expert. Systematically diagnose issues, identify root causes, and suggest minimal fixes. Always verify your assumptions.",
        "tools_enabled": ["file_read", "grep", "bash"],
        "category": "Development",
        "icon": "🐛",
    },
    {
        "id": "architect",
        "name": "Software Architect",
        "description": "Designs system architecture and makes architectural decisions",
        "agent_type": "react",
        "model": "gpt-4",
        "provider": "openai",
        "max_steps": 12,
        "temperature": 0.7,
        "system_prompt": "You are a senior software architect. Design scalable, maintainable systems. Consider trade-offs and document architectural decisions.",
        "tools_enabled": ["file_read", "grep", "glob"],
        "category": "Design",
        "icon": "🏗️",
    },
    {
        "id": "refactorer",
        "name": "Refactoring Expert",
        "description": "Improves code structure without changing behavior",
        "agent_type": "react",
        "model": "gpt-4",
        "provider": "openai",
        "max_steps": 15,
        "temperature": 0.3,
        "system_prompt": "You are a refactoring specialist. Improve code readability, reduce complexity, and apply design patterns while preserving behavior.",
        "tools_enabled": ["file_read", "file_write", "grep"],
        "category": "Development",
        "icon": "♻️",
    },
    {
        "id": "test-writer",
        "name": "Test Writer",
        "description": "Creates comprehensive test suites",
        "agent_type": "react",
        "model": "gpt-4",
        "provider": "openai",
        "max_steps": 18,
        "temperature": 0.5,
        "system_prompt": "You are an expert test engineer. Write thorough unit, integration, and end-to-end tests. Cover edge cases and error scenarios.",
        "tools_enabled": ["file_read", "file_write", "bash"],
        "category": "Testing",
        "icon": "🧪",
    },
    {
        "id": "doc-writer",
        "name": "Documentation Writer",
        "description": "Creates comprehensive documentation for code",
        "agent_type": "react",
        "model": "gpt-4",
        "provider": "openai",
        "max_steps": 10,
        "temperature": 0.7,
        "system_prompt": "You are a technical writer. Create clear, comprehensive documentation including API docs, READMEs, and inline comments.",
        "tools_enabled": ["file_read", "file_write", "grep"],
        "category": "Documentation",
        "icon": "📝",
    },
    {
        "id": "security-auditor",
        "name": "Security Auditor",
        "description": "Identifies security vulnerabilities in code",
        "agent_type": "react",
        "model": "gpt-4",
        "provider": "openai",
        "max_steps": 15,
        "temperature": 0.2,
        "system_prompt": "You are a security expert. Identify vulnerabilities including SQL injection, XSS, CSRF, authentication flaws, and insecure configurations.",
        "tools_enabled": ["file_read", "grep", "glob"],
        "category": "Security",
        "icon": "🛡️",
    },
    {
        "id": "performance-analyst",
        "name": "Performance Analyst",
        "description": "Analyzes and optimizes code performance",
        "agent_type": "react",
        "model": "gpt-4",
        "provider": "openai",
        "max_steps": 15,
        "temperature": 0.3,
        "system_prompt": "You are a performance optimization expert. Identify bottlenecks, suggest improvements, and optimize algorithms.",
        "tools_enabled": ["file_read", "grep", "bash"],
        "category": "Optimization",
        "icon": "⚡",
    },
]


# ── CRUD Endpoints ───────────────────────────────────────────────────────────


@router.post("", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    request: AgentCreateRequest,
    db: AsyncSession = Depends(get_db),
    user: Any = Depends(require_permission(Resource.AGENTS, Action.CREATE)),
) -> AgentResponse:
    # If template_id provided, apply template defaults
    template = None
    if request.template_id:
        template = next((t for t in AGENT_TEMPLATES if t["id"] == request.template_id), None)
        if not template:
            raise HTTPException(status_code=400, detail=f"Template '{request.template_id}' not found")

    agent_type = request.agent_type or (template["agent_type"] if template else "react")
    model = request.model or (template["model"] if template else None)
    provider = request.provider or (template["provider"] if template else None)
    max_steps = request.max_steps or (template["max_steps"] if template else 10)
    temperature = (
        request.temperature
        if request.temperature is not None
        else (template["temperature"] if template else 0.7)
    )
    system_prompt = request.system_prompt or (template["system_prompt"] if template else None)
    tools_enabled = request.tools_enabled or (template["tools_enabled"] if template else None)

    project_id = await _resolve_project_id(db, str(user.id))
    service = AgentService(db)
    try:
        agent = await service.create_agent(
            project_id=project_id,
            created_by=str(user.id),
            name=request.name,
            type=_db_type_for(agent_type),
            description=request.description or (template["description"] if template else ""),
            config={
                "agent_type": agent_type,
                "max_steps": max_steps,
                "temperature": temperature,
                "template_id": request.template_id,
            },
            system_prompt=system_prompt,
            model_provider=provider,
            model_name=model,
            tools=tools_enabled or [s["name"] for s in tool_registry.get_schemas()],
            is_active=True,
        )
    except (ValueError, AgentExecutionException) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return _agent_response(agent)


@router.get("", response_model=list[AgentResponse])
async def list_agents(
    db: AsyncSession = Depends(get_db),
) -> list[AgentResponse]:
    service = AgentService(db)
    agents, _ = await service.list_agents(page=1, page_size=1000)
    return [_agent_response(a) for a in agents]


@router.get("/templates", response_model=list[AgentTemplateResponse])
async def list_agent_templates():
    """Get available agent templates."""
    return [
        AgentTemplateResponse(
            id=t["id"],
            name=t["name"],
            description=t["description"],
            agent_type=t["agent_type"],
            model=t["model"],
            provider=t["provider"],
            max_steps=t["max_steps"],
            temperature=t["temperature"],
            system_prompt=t["system_prompt"],
            tools_enabled=t["tools_enabled"],
            category=t["category"],
            icon=t["icon"],
        )
        for t in AGENT_TEMPLATES
    ]


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str,
    db: AsyncSession = Depends(get_db),
) -> AgentResponse:
    service = AgentService(db)
    try:
        agent = await service.get_agent(agent_id)
    except AgentNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    return _agent_response(agent)


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    request: AgentUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _user: Any = Depends(require_permission(Resource.AGENTS, Action.UPDATE)),
) -> AgentResponse:
    service = AgentService(db)
    try:
        agent = await service.get_agent(agent_id)
    except AgentNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

    config = dict(agent.config or {})
    updates: dict[str, Any] = {}
    if request.name is not None:
        updates["name"] = request.name
    if request.description is not None:
        updates["description"] = request.description
    if request.model is not None:
        updates["model_name"] = request.model
    if request.provider is not None:
        updates["model_provider"] = request.provider
    if request.system_prompt is not None:
        updates["system_prompt"] = request.system_prompt
    if request.max_steps is not None:
        config["max_steps"] = request.max_steps
    if request.temperature is not None:
        config["temperature"] = request.temperature
    if request.tools_enabled is not None:
        updates["tools"] = request.tools_enabled

    updates["config"] = config
    updated = await service.update_agent(agent_id, **updates)
    return _agent_response(updated)


@router.post("/{agent_id}/start", response_model=AgentResponse)
async def start_agent(
    agent_id: str,
    db: AsyncSession = Depends(get_db),
    _user: Any = Depends(require_permission(Resource.AGENTS, Action.UPDATE)),
) -> AgentResponse:
    service = AgentService(db)
    try:
        updated = await service.update_agent(agent_id, is_active=True)
    except AgentNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    return _agent_response(updated)


@router.post("/{agent_id}/stop", response_model=AgentResponse)
async def stop_agent(
    agent_id: str,
    db: AsyncSession = Depends(get_db),
    _user: Any = Depends(require_permission(Resource.AGENTS, Action.UPDATE)),
) -> AgentResponse:
    service = AgentService(db)
    try:
        updated = await service.update_agent(agent_id, is_active=False)
    except AgentNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    return _agent_response(updated)


@router.post("/{agent_id}/execute", response_model=AgentExecuteResponse)
async def execute_agent(
    agent_id: str,
    request: AgentExecuteRequest,
    db: AsyncSession = Depends(get_db),
    user: Any = Depends(require_permission(Resource.AGENTS, Action.EXECUTE)),
) -> AgentExecuteResponse:
    service = AgentService(db)
    try:
        agent = await service.get_agent(agent_id)
    except AgentNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

    if not agent.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Agent is not active")

    execution = await service.execute_agent(
        agent_id=agent_id,
        task=request.input,
        context=request.context,
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

    result = await react_agent.run(request.input, request.context)

    tokens_used = 0
    if result.token_usage:
        tokens_used = int(result.token_usage.get("total_tokens", 0) or 0)

    await service.complete_execution(
        str(execution.id),
        result={"output": result.output, "steps": len(result.steps), "tool_calls": len(result.tool_calls)},
        error=result.error,
        tokens_used=tokens_used,
    )

    return AgentExecuteResponse(
        execution_id=str(execution.id),
        agent_id=agent_id,
        output=result.output,
        steps=[
            {"thought": s.thought, "action": s.action, "observation": s.observation}
            for s in result.steps
        ],
        tool_calls=[
            {"name": tc.name, "arguments": tc.arguments, "result": tc.result, "error": tc.error}
            for tc in result.tool_calls
        ],
        execution_time_ms=result.execution_time_ms,
        error=result.error,
    )


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: str,
    db: AsyncSession = Depends(get_db),
    _user: Any = Depends(require_permission(Resource.AGENTS, Action.DELETE)),
) -> None:
    service = AgentService(db)
    try:
        deleted = await service.delete_agent(agent_id)
    except AgentNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
