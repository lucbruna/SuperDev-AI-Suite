from __future__ import annotations

from typing import Final

DEFAULT_MODELS: Final[dict[str, str]] = {
    "openai": "gpt-4o",
    "anthropic": "claude-3-5-sonnet-20241022",
    "gemini": "gemini-1.5-pro",
    "ollama": "llama3",
    "openrouter": "openrouter/auto",
}

PROVIDER_NAMES: Final[list[str]] = [
    "openai",
    "anthropic",
    "gemini",
    "ollama",
    "openrouter",
]

CAPABILITY_NAMES: Final[list[str]] = [
    "chat",
    "stream",
    "embeddings",
    "vision",
    "tools",
    "code_execution",
]

AGENT_CATEGORIES: Final[list[str]] = [
    "coding",
    "review",
    "planning",
    "research",
    "deployment",
    "testing",
    "security",
    "documentation",
    "monitoring",
]

EVENT_TYPES: Final[list[str]] = [
    "model_called",
    "stream_started",
    "stream_chunk",
    "stream_completed",
    "agent_started",
    "agent_completed",
    "agent_failed",
    "tool_called",
    "tool_completed",
    "tool_failed",
    "error_occurred",
    "warning_issued",
    "permission_checked",
]

DEFAULT_TIMEOUT: Final[int] = 60
DEFAULT_MAX_RETRIES: Final[int] = 3
DEFAULT_MAX_TOKENS: Final[int] = 4096
DEFAULT_TEMPERATURE: Final[float] = 0.7
DEFAULT_EMBEDDING_DIMENSION: Final[int] = 1536
MAX_CONCURRENT_AGENTS: Final[int] = 10
TOKEN_LIMIT_PER_MINUTE: Final[int] = 100000
REQUEST_LIMIT_PER_MINUTE: Final[int] = 1000
MAX_TOOL_CALLS_PER_STEP: Final[int] = 10
MAX_CONTEXT_LENGTH: Final[int] = 128000

LOG_LEVELS: Final[list[str]] = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

COST_PER_TOKEN: Final[dict[str, dict[str, float]]] = {
    "gpt-4o": {"input": 0.00001, "output": 0.00003},
    "gpt-4o-mini": {"input": 0.0000015, "output": 0.000006},
    "claude-3-5-sonnet-20241022": {"input": 0.000003, "output": 0.000015},
    "claude-3-haiku": {"input": 0.00000025, "output": 0.00000125},
    "gemini-1.5-pro": {"input": 0.0000035, "output": 0.0000105},
    "gemini-1.5-flash": {"input": 0.00000035, "output": 0.00000105},
    "llama3": {"input": 0.0, "output": 0.0},
}

VERSION: Final[str] = "2.0.0"
