from __future__ import annotations


class AIEngineError(Exception):
    """Base exception for all AI Engine errors."""

    def __init__(self, message: str = "AI Engine error", *, code: str | None = None):
        self.code = code or self.__class__.__name__
        super().__init__(message)


class ProviderError(AIEngineError):
    """Base provider error."""


class ProviderNotFoundError(ProviderError):
    """Raised when a provider is not found."""


class ProviderTimeoutError(ProviderError):
    """Raised when a provider request times out."""


class ProviderAuthError(ProviderError):
    """Raised when provider authentication fails."""


class ProviderRateLimitError(ProviderError):
    """Raised when provider rate limit is exceeded."""


class ModelNotFoundError(AIEngineError):
    """Raised when a model is not found."""


class ModelNotSupportedError(AIEngineError):
    """Raised when a model is not supported by the provider."""


class AgentError(AIEngineError):
    """Base agent error."""


class AgentExecutionError(AgentError):
    """Raised when agent execution fails."""


class AgentTimeoutError(AgentError):
    """Raised when an agent times out."""


class AgentNotFoundError(AgentError):
    """Raised when an agent is not found."""


class ConfigurationError(AIEngineError):
    """Raised when configuration is invalid."""


class PermissionError(AIEngineError):
    """Raised when a permission check fails."""


class ContextError(AIEngineError):
    """Raised when a context operation fails."""


class TokenLimitError(AIEngineError):
    """Raised when token limit is exceeded."""


class EmbeddingError(AIEngineError):
    """Raised when an embedding operation fails."""


class RegistryError(AIEngineError):
    """Raised when a registry operation fails."""


class RuntimeError(AIEngineError):
    """Raised when a runtime operation fails."""


class EngineNotInitializedError(AIEngineError):
    """Raised when the engine is used before initialization."""
