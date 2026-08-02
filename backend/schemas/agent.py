from __future__ import annotations

from datetime import datetime

from pydantic import AliasChoices, BaseModel, Field

from backend.schemas.base import BaseSchema


class AgentCreateRequest(BaseModel):
    """Request to create a new agent."""

    name: str = Field(..., min_length=1, max_length=255, description="Agent name")
    agent_type: str = Field(
        "react",
        description="Agent type: react, planner_executor, code, review, chat",
    )
    description: str = Field("", description="Agent description")
    model: str | None = Field(None, description="LLM model name")
    provider: str | None = Field(None, description="LLM provider name")
    max_steps: int = Field(10, ge=1, le=100, description="Maximum reasoning steps")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Model temperature")
    system_prompt: str | None = Field(None, description="System prompt")
    tools_enabled: list[str] | None = Field(
        None, description="Tool names to enable (all if unset)"
    )
    template_id: str | None = Field(None, description="Template ID to apply defaults from")


# Backwards-compatible alias for older import sites.
AgentCreate = AgentCreateRequest


class AgentUpdateRequest(BaseModel):
    """Request to update agent fields."""

    name: str | None = Field(None, min_length=1, max_length=255, description="Agent name")
    description: str | None = Field(None, description="Agent description")
    model: str | None = Field(None, description="LLM model name")
    provider: str | None = Field(None, description="LLM provider name")
    max_steps: int | None = Field(None, ge=1, le=100, description="Maximum reasoning steps")
    temperature: float | None = Field(None, ge=0.0, le=2.0, description="Model temperature")
    system_prompt: str | None = Field(None, description="System prompt")
    tools_enabled: list[str] | None = Field(None, description="Tool names to enable")


# Backwards-compatible alias for older import sites.
AgentUpdate = AgentUpdateRequest


class AgentExecuteRequest(BaseModel):
    """Request to execute an agent task.

    Accepts both ``task`` (canonical) and the legacy ``input`` field so old
    clients keep working; callers should use ``request.task``.
    """

    task: str = Field(
        ...,
        min_length=1,
        validation_alias=AliasChoices("task", "input"),
        description="Task description for the agent",
    )
    context: dict | None = Field(None, description="Additional execution context")


class AgentResponse(BaseModel):
    """Agent response — matches the API AgentResponse contract exactly."""

    id: str = Field(..., description="Agent UUID")
    name: str = Field(..., description="Agent name")
    description: str = Field("", description="Agent description")
    agent_type: str = Field(..., description="Agent type")
    status: str = Field("idle", description="Agent status: idle, running, error")
    tools: list[dict] = Field(
        default_factory=list, description="Tool schemas (name, description, parameters)"
    )
    model: str | None = Field(None, description="LLM model name")
    provider: str | None = Field(None, description="LLM provider name")
    max_steps: int = Field(10, description="Maximum reasoning steps")
    temperature: float = Field(0.7, description="Model temperature")
    system_prompt: str | None = Field(None, description="System prompt")
    template_id: str | None = Field(None, description="Template ID")


class AgentTemplateResponse(BaseModel):
    """Agent template summary."""

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
    """Result of a synchronous agent execution."""

    execution_id: str
    agent_id: str
    output: str
    steps: list[dict]
    tool_calls: list[dict]
    execution_time_ms: float
    error: str | None = None


class AgentExecutionResponse(BaseSchema):
    """Agent execution record (persisted) response."""

    id: str = Field(..., description="Execution UUID")
    agent_id: str = Field(..., description="Agent UUID")
    run_id: str | None = Field(None, description="Workflow run UUID if triggered by workflow")
    task: str = Field(..., description="Task description")
    context: dict = Field(default_factory=dict, description="Execution context")
    status: str = Field(..., description="Execution status: idle, running, completed, failed")
    result: dict | None = Field(None, description="Execution result")
    error: str | None = Field(None, description="Error message if failed")
    tokens_used: int = Field(0, description="Total tokens consumed")
    cost_usd: float = Field(0.0, description="Total cost in USD")
    started_at: datetime | None = Field(None, description="Execution start timestamp")
    completed_at: datetime | None = Field(None, description="Execution completion timestamp")
    created_at: datetime | None = Field(None, description="Record creation timestamp")
