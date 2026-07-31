from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ProviderState(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"


@dataclass
class LLMRequest:
    """Represents a single LLM request."""

    provider: str
    model: str
    prompt: str
    params: dict[str, Any] = field(default_factory=dict)
    max_tokens: int = 1024
    temperature: float = 0.7
    request_id: str = ""
    created_at: float = field(default_factory=time.time)


@dataclass
class LLMResponse:
    """Represents a single LLM response."""

    request_id: str
    provider: str
    model: str
    content: str
    tokens_prompt: int = 0
    tokens_completion: int = 0
    latency_ms: float = 0.0
    cost_usd: float = 0.0
    finish_reason: str = "stop"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ProviderInfo:
    """Information about a registered LLM provider."""

    name: str
    model: str
    state: ProviderState = ProviderState.ACTIVE
    capabilities: list[str] = field(default_factory=list)
    cost_per_token: float = 0.0
    latency_p50: float = 0.0
    max_tokens: int = 4096
    supports_streaming: bool = True
    supports_functions: bool = False
    supports_vision: bool = False
    registered_at: float = field(default_factory=time.time)


@dataclass
class LLMContext:
    """Context passed during LLM execution."""

    request_id: str
    user_id: str = ""
    session_id: str = ""
    conversation_id: str = ""
    environment: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    permissions: list[str] = field(default_factory=list)


@dataclass
class TokenUsage:
    """Token usage statistics."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0

    def __post_init__(self) -> None:
        self.total_tokens = self.prompt_tokens + self.completion_tokens


@dataclass
class LLMMetrics:
    """Metrics for a single LLM operation."""

    provider: str = ""
    model: str = ""
    latency_ms: float = 0.0
    tokens_prompt: int = 0
    tokens_completion: int = 0
    cost_usd: float = 0.0
    success: bool = False
    error: str = ""
    timestamp: float = field(default_factory=time.time)
