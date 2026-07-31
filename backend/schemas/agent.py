from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from backend.schemas.base import BaseSchema


class AgentBase(BaseSchema):
    """Base agent fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Agent name")
    type: str = Field(
        ..., description="Agent type: planner, executor, reviewer, tester, architect, researcher, security, deployment"
    )
    description: str | None = Field(None, description="Agent description")
    config: dict = Field(default_factory=dict, description="Agent configuration JSON")
    system_prompt: str | None = Field(None, description="System prompt for the agent")
    model_provider: str | None = Field(None, max_length=50, description="LLM provider name")
    model_name: str | None = Field(None, max_length=100, description="LLM model name")
    tools: list[str] = Field(default_factory=list, description="Tool names available to the agent")


class AgentCreate(BaseModel):
    """Request to create a new agent."""

    project_id: str = Field(..., description="Project UUID")
    name: str = Field(..., min_length=1, max_length=255, description="Agent name")
    type: str = Field(..., description="Agent type")
    description: str | None = Field(None, description="Agent description")
    config: dict = Field(default_factory=dict, description="Agent configuration")
    system_prompt: str | None = Field(None, description="System prompt")
    model_provider: str | None = Field(None, description="LLM provider name")
    model_name: str | None = Field(None, description="LLM model name")
    tools: list[str] = Field(default_factory=list, description="Available tool names")


class AgentUpdate(BaseModel):
    """Request to update agent fields."""

    name: str | None = Field(None, min_length=1, max_length=255, description="Agent name")
    description: str | None = Field(None, description="Agent description")
    config: dict | None = Field(None, description="Agent configuration")
    system_prompt: str | None = Field(None, description="System prompt")
    is_active: bool | None = Field(None, description="Whether the agent is active")


class AgentResponse(BaseSchema):
    """Full agent response."""

    id: str = Field(..., description="Agent UUID")
    project_id: str = Field(..., description="Project UUID")
    name: str = Field(..., description="Agent name")
    type: str = Field(..., description="Agent type")
    description: str | None = Field(None, description="Agent description")
    config: dict = Field(default_factory=dict, description="Agent configuration")
    system_prompt: str | None = Field(None, description="System prompt")
    model_provider: str | None = Field(None, description="LLM provider name")
    model_name: str | None = Field(None, description="LLM model name")
    tools: list[str] = Field(default_factory=list, description="Available tools")
    is_active: bool = Field(True, description="Whether the agent is active")
    created_by: str = Field(..., description="Creator user UUID")
    created_at: datetime | None = Field(None, description="Creation timestamp")
    updated_at: datetime | None = Field(None, description="Last update timestamp")


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
