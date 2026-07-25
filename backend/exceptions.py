from __future__ import annotations

from typing import Any


class AppException(Exception):
    def __init__(
        self,
        message: str = "An application error occurred",
        code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundException(AppException):
    def __init__(self, message: str = "Resource not found", details: dict[str, Any] | None = None) -> None:
        super().__init__(message=message, code="NOT_FOUND", status_code=404, details=details)


class ValidationException(AppException):
    def __init__(self, message: str = "Validation failed", details: dict[str, Any] | None = None) -> None:
        super().__init__(message=message, code="VALIDATION_ERROR", status_code=422, details=details)


class AuthenticationException(AppException):
    def __init__(self, message: str = "Authentication failed", details: dict[str, Any] | None = None) -> None:
        super().__init__(message=message, code="AUTHENTICATION_ERROR", status_code=401, details=details)


class AuthorizationException(AppException):
    def __init__(self, message: str = "Access denied", details: dict[str, Any] | None = None) -> None:
        super().__init__(message=message, code="AUTHORIZATION_ERROR", status_code=403, details=details)


class ConfigurationException(AppException):
    def __init__(self, message: str = "Configuration error", details: dict[str, Any] | None = None) -> None:
        super().__init__(message=message, code="CONFIGURATION_ERROR", status_code=500, details=details)


class PluginException(AppException):
    def __init__(self, message: str = "Plugin error", details: dict[str, Any] | None = None) -> None:
        super().__init__(message=message, code="PLUGIN_ERROR", status_code=500, details=details)


class ProviderException(AppException):
    def __init__(self, message: str = "Provider error", details: dict[str, Any] | None = None) -> None:
        super().__init__(message=message, code="PROVIDER_ERROR", status_code=502, details=details)


class WorkflowException(AppException):
    def __init__(self, message: str = "Workflow error", details: dict[str, Any] | None = None) -> None:
        super().__init__(message=message, code="WORKFLOW_ERROR", status_code=500, details=details)


class RuntimeException(AppException):
    def __init__(self, message: str = "Runtime error", details: dict[str, Any] | None = None) -> None:
        super().__init__(message=message, code="RUNTIME_ERROR", status_code=500, details=details)


class DatabaseException(AppException):
    def __init__(self, message: str = "Database error", details: dict[str, Any] | None = None) -> None:
        super().__init__(message=message, code="DATABASE_ERROR", status_code=500, details=details)


class SecurityException(AppException):
    def __init__(self, message: str = "Security violation", details: dict[str, Any] | None = None) -> None:
        super().__init__(message=message, code="SECURITY_ERROR", status_code=403, details=details)


class StorageException(AppException):
    def __init__(self, message: str = "Storage error", details: dict[str, Any] | None = None) -> None:
        super().__init__(message=message, code="STORAGE_ERROR", status_code=500, details=details)