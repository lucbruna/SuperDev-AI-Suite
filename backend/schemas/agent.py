from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from backend.schemas.base import BaseSchema


class AgentCreate(BaseModel):
    """Request to create a new agent — matches the API AgentCreateRequest contract."""

    name: str = Field(..., min_length=1, max_length=255, description="Agent name")
    agent_type: str = Field("react", description="Agent type: react, planner_executor, code, review, chat")
    description: str = Field("", description="Agent description")
    model: str | None = Field(None, description="LLM model name")
    provider: str | None = Field(None, description="LLM provider name")
    max_steps: int = Field(10, ge=1, le=100, description="Maximum reasoning steps")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Model temperature")
    system_prompt: str | None = Field(None, description="System prompt")
    tools_enabled: list[str] | None = Field(None, description="Tool names to enable (all if unset)")
    template_id: str | None = Field(None, description="Template ID to apply defaults from")


class AgentUpdate(BaseModel):
    """Request to update agent fields — matches the API AgentUpdateRequest contract."""

    name: str | None = Field(None, min_length=1, max_length=255, description="Agent name")
    description: str | None = Field(None, description="Agent description")
    model: str | None = Field(None, description="LLM model name")
    provider: str | None = Field(None, description="LLM provider name")
    max_steps: int | None = Field(None, ge=1, le=100, description="Maximum reasoning steps")
    temperature: float | None = Field(None, ge=0.0, le=2.0, description="Model temperature")
    system_prompt: str | None = Field(None, description="System prompt")
    tools_enabled: list[str] | None = Field(None, description="Tool names to enable")


class AgentResponse(BaseModel):
    """Agent response — matches the API AgentResponse contract exactly."""

    id: str = Field(..., description="Agent UUID")
    name: str = Field(..., description="Agent name")
    description: str = Field("", description="Agent description")
    agent_type: str = Field(..., description="Agent type")
    status: str = Field("idle", description="Agent status: idle, running, error")
    tools: list[dict] = Field(default_factory=list, description="Tool schemas (name, description, parameters)")
    model: str | None = Field(None, description="LLM model name")
    provider: str | None = Field(None, description="LLM provider name")
    max_steps: int = Field(10, description="Maximum reasoning steps")
    temperature: float = Field(0.7, description="Model temperature")
    system_prompt: str | None = Field(None, description="System prompt")
    template_id: str | None = Field(None, description="Template ID")


class AgentExecuteRequest(BaseModel):
    """Request to execute an agent task."""

    task: str = Field(..., min_length=1, description="Task description for the agent")
    context: dict = Field(default_factory=dict, description="Additional execution context")


class AgentExecutionResponse(BaseSchema):
    """Agent execution result response."""

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
