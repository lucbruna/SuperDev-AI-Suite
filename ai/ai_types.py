from __future__ import annotations

from typing import Any, Literal, TypedDict, TypeAlias

ProviderType: TypeAlias = Literal[
    "openai", "anthropic", "gemini", "ollama", "openrouter"
]
ModelCapability: TypeAlias = Literal[
    "chat", "stream", "embeddings", "vision", "tools", "code_execution"
]
AgentRole: TypeAlias = Literal[
    "coder", "reviewer", "planner", "researcher",
    "deployer", "tester", "security", "documentation",
]
AgentStatus: TypeAlias = Literal[
    "idle", "running", "paused", "completed", "failed", "cancelled"
]
EventType: TypeAlias = Literal[
    "model_called", "stream_started", "stream_chunk", "stream_completed",
    "agent_started", "agent_completed", "agent_failed",
    "tool_called", "tool_completed", "tool_failed",
    "error_occurred", "warning_issued",
]
PermissionLevel: TypeAlias = Literal["admin", "user", "viewer", "none"]


class MessageDict(TypedDict, total=False):
    role: str
    content: str
    name: str | None
    tool_calls: list[dict[str, Any]] | None
    tool_call_id: str | None


class ModelConfigDict(TypedDict, total=False):
    provider: str
    model: str
    temperature: float
    max_tokens: int
    timeout: int
    stream: bool


class AgentConfigDict(TypedDict, total=False):
    name: str
    role: AgentRole
    model: str
    provider: str
    instructions: str
    tools: list[str]
    max_iterations: int
    timeout: int


class ToolCallDict(TypedDict):
    id: str
    name: str
    arguments: dict[str, Any]


class UsageDict(TypedDict, total=False):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost: float


class HealthStatusDict(TypedDict, total=False):
    status: str
    provider: str
    latency_ms: float
    model: str
    error: str | None
    timestamp: str
