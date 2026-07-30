from __future__ import annotations


class ReasoningError(Exception):
    """Base error for the reasoning module."""


class ReasoningContextError(ReasoningError):
    """Raised when reasoning context is invalid."""


class ReasoningEngineError(ReasoningError):
    """Raised when the reasoning engine encounters an error."""


class ReasoningValidationError(ReasoningError):
    """Raised when reasoning output fails validation."""


class ReasoningTimeoutError(ReasoningError):
    """Raised when a reasoning operation exceeds its time limit."""


class ReasoningPermissionError(ReasoningError):
    """Raised when the caller lacks permission for a reasoning operation."""


class ReasoningResourceError(ReasoningError):
    """Raised when required resources are unavailable."""
