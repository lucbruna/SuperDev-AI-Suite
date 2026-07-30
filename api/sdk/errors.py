from __future__ import annotations


class SDKError(Exception):
    """Base exception for all SDK errors."""

    def __init__(self, message: str, status_code: int = 0, details: str | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.details = details


class ConnectionError(SDKError):
    """Failed to connect to the server."""


class AuthenticationError(SDKError):
    """Authentication failed (invalid credentials, expired token)."""


class AuthorizationError(SDKError):
    """Insufficient permissions for the requested operation."""


class NotFoundError(SDKError):
    """Requested resource was not found."""


class ValidationError(SDKError):
    """Request payload failed validation."""


class RateLimitError(SDKError):
    """Too many requests — rate limit exceeded."""


class TimeoutError(SDKError):
    """Request timed out."""


class ServerError(SDKError):
    """Internal server error."""
