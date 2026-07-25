"""Exception classes for the SuperDev Python SDK."""

from __future__ import annotations

from typing import Any


class SuperDevError(Exception):
    """Base exception for all SuperDev SDK errors."""

    def __init__(
        self,
        message: str = "An error occurred",
        status_code: int = 0,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.details = details or {}


class AuthenticationError(SuperDevError):
    """Raised when authentication fails (401)."""

    def __init__(self, message: str = "Authentication failed", **kwargs: Any) -> None:
        super().__init__(message, status_code=401, **kwargs)


class AuthorizationError(SuperDevError):
    """Raised when authorization fails (403)."""

    def __init__(self, message: str = "Authorization denied", **kwargs: Any) -> None:
        super().__init__(message, status_code=403, **kwargs)


class NotFoundError(SuperDevError):
    """Raised when a resource is not found (404)."""

    def __init__(self, message: str = "Resource not found", **kwargs: Any) -> None:
        super().__init__(message, status_code=404, **kwargs)


class ValidationError(SuperDevError):
    """Raised when request validation fails (422)."""

    def __init__(self, message: str = "Validation error", **kwargs: Any) -> None:
        super().__init__(message, status_code=422, **kwargs)


class RateLimitError(SuperDevError):
    """Raised when rate limit is exceeded (429)."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: float | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, status_code=429, **kwargs)
        self.retry_after = retry_after


class ServerError(SuperDevError):
    """Raised when server returns 5xx error."""

    def __init__(self, message: str = "Server error", **kwargs: Any) -> None:
        super().__init__(message, status_code=500, **kwargs)


class ConnectionError(SuperDevError):
    """Raised when connection to the server fails."""

    def __init__(self, message: str = "Connection failed", **kwargs: Any) -> None:
        super().__init__(message, status_code=0, **kwargs)


class TimeoutError(SuperDevError):
    """Raised when a request times out."""

    def __init__(self, message: str = "Request timed out", **kwargs: Any) -> None:
        super().__init__(message, status_code=0, **kwargs)
