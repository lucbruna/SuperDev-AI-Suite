from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AIModel(BaseModel):
    """AI model descriptor."""

    name: str
    provider: str
    capabilities: list[str] = []
    context_length: int = 128000
    max_output_tokens: int = 4096
    cost_per_input_token: float = 0.0
    cost_per_output_token: float = 0.0
    is_default: bool = False


class AgentConfig(BaseModel):
    """Configuration for an AI agent."""

    name: str
    role: str = "coder"
    model: str = "gpt-4o"
    provider: str = "openai"
    instructions: str = ""
    tools: list[str] = Field(default_factory=list)
    max_iterations: int = 10
    timeout: int = 120
    temperature: float = 0.7
    max_tokens: int = 4096


class SessionConfig(BaseModel):
    """Configuration for an AI session."""

    session_id: str
    provider: str = "openai"
    model: str = "gpt-4o"
    temperature: float = 0.7
    max_tokens: int = 4096
    stream: bool = False
    system_prompt: str | None = None


class RoutingConfig(BaseModel):
    """Configuration for AI request routing."""

    preferred_provider: str | None = None
    fallback_providers: list[str] = Field(default_factory=lambda: ["openai", "anthropic", "gemini"])
    cost_optimize: bool = False
    latency_optimize: bool = True
    model_selector: str = "auto"


class Message(BaseModel):
    """A chat message."""

    role: str
    content: str
    name: str | None = None
    tool_calls: list[dict[str, Any]] | None = None
    tool_call_id: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now())


class Conversation(BaseModel):
    """A conversation thread."""

    id: str
    messages: list[Message] = Field(default_factory=list)
    session_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


class ModelResponse(BaseModel):
    """Response from a model invocation."""

    content: str
    model: str
    provider: str
    usage: dict[str, int] = Field(default_factory=dict)
    cost: float = 0.0
    latency_ms: float = 0.0
    finish_reason: str = "stop"
    tool_calls: list[dict[str, Any]] | None = None


class ProviderStatus(BaseModel):
    """Status of an AI provider."""

    name: str
    available: bool = False
    latency_ms: float = 0.0
    models: list[str] = Field(default_factory=list)
    error: str | None = None
    last_check: datetime = Field(default_factory=lambda: datetime.now())


class EngineHealth(BaseModel):
    """Health status of the AI engine."""

    status: str = "healthy"
    initialized: bool = False
    providers: list[ProviderStatus] = Field(default_factory=list)
    active_agents: int = 0
    active_sessions: int = 0
    uptime_seconds: float = 0.0
    version: str = "2.0.0"
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
