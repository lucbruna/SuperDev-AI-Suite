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
    def __init__(
        self,
        message: str = "Resource not found",
        details: dict[str, Any] | None = None,
        code: str = "NOT_FOUND",
        status_code: int = 404,
    ) -> None:
        super().__init__(message=message, code=code, status_code=status_code, details=details)


class ValidationException(AppException):
    def __init__(
        self,
        message: str = "Validation failed",
        details: dict[str, Any] | None = None,
        code: str = "VALIDATION_ERROR",
        status_code: int = 422,
    ) -> None:
        super().__init__(message=message, code=code, status_code=status_code, details=details)


class AuthenticationException(AppException):
    def __init__(
        self,
        message: str = "Authentication failed",
        details: dict[str, Any] | None = None,
        code: str = "AUTHENTICATION_ERROR",
        status_code: int = 401,
    ) -> None:
        super().__init__(message=message, code=code, status_code=status_code, details=details)


class AuthorizationException(AppException):
    def __init__(
        self,
        message: str = "Access denied",
        details: dict[str, Any] | None = None,
        code: str = "AUTHORIZATION_ERROR",
        status_code: int = 403,
    ) -> None:
        super().__init__(message=message, code=code, status_code=status_code, details=details)


class ConfigurationException(AppException):
    def __init__(
        self,
        message: str = "Configuration error",
        details: dict[str, Any] | None = None,
        code: str = "CONFIGURATION_ERROR",
        status_code: int = 500,
    ) -> None:
        super().__init__(message=message, code=code, status_code=status_code, details=details)


class PluginException(AppException):
    def __init__(
        self,
        message: str = "Plugin error",
        details: dict[str, Any] | None = None,
        code: str = "PLUGIN_ERROR",
        status_code: int = 500,
    ) -> None:
        super().__init__(message=message, code=code, status_code=status_code, details=details)


class ProviderException(AppException):
    def __init__(
        self,
        message: str = "Provider error",
        details: dict[str, Any] | None = None,
        code: str = "PROVIDER_ERROR",
        status_code: int = 502,
    ) -> None:
        super().__init__(message=message, code=code, status_code=status_code, details=details)


class WorkflowException(AppException):
    def __init__(
        self,
        message: str = "Workflow error",
        details: dict[str, Any] | None = None,
        code: str = "WORKFLOW_ERROR",
        status_code: int = 500,
    ) -> None:
        super().__init__(message=message, code=code, status_code=status_code, details=details)


class RuntimeException(AppException):
    def __init__(
        self,
        message: str = "Runtime error",
        details: dict[str, Any] | None = None,
        code: str = "RUNTIME_ERROR",
        status_code: int = 500,
    ) -> None:
        super().__init__(message=message, code=code, status_code=status_code, details=details)


class DatabaseException(AppException):
    def __init__(
        self,
        message: str = "Database error",
        details: dict[str, Any] | None = None,
        code: str = "DATABASE_ERROR",
        status_code: int = 500,
    ) -> None:
        super().__init__(message=message, code=code, status_code=status_code, details=details)


class SecurityException(AppException):
    def __init__(
        self,
        message: str = "Security violation",
        details: dict[str, Any] | None = None,
        code: str = "SECURITY_ERROR",
        status_code: int = 403,
    ) -> None:
        super().__init__(message=message, code=code, status_code=status_code, details=details)


class StorageException(AppException):
    def __init__(
        self,
        message: str = "Storage error",
        details: dict[str, Any] | None = None,
        code: str = "STORAGE_ERROR",
        status_code: int = 500,
    ) -> None:
        super().__init__(message=message, code=code, status_code=status_code, details=details)


# ── User Exceptions ───────────────────────────────────────────────


class UserNotFoundException(NotFoundException):
    def __init__(self, identifier: str = "User") -> None:
        super().__init__(message=f"{identifier} not found", code="USER_NOT_FOUND")


class UserAlreadyExistsException(AppException):
    def __init__(self, field: str = "email") -> None:
        super().__init__(message=f"User with this {field} already exists", code="USER_ALREADY_EXISTS", status_code=409)


class UserInactiveException(AppException):
    def __init__(self) -> None:
        super().__init__(message="User account is inactive", code="USER_INACTIVE", status_code=403)


class InvalidCredentialsException(AuthenticationException):
    def __init__(self) -> None:
        super().__init__(message="Invalid email or password", code="INVALID_CREDENTIALS")


class TokenExpiredException(AuthenticationException):
    def __init__(self) -> None:
        super().__init__(message="Token has expired", code="TOKEN_EXPIRED")


class TokenInvalidException(AuthenticationException):
    def __init__(self) -> None:
        super().__init__(message="Invalid token", code="TOKEN_INVALID")


class MFARequiredException(AuthenticationException):
    def __init__(self) -> None:
        super().__init__(message="MFA verification required", code="MFA_REQUIRED")


# ── Project Exceptions ────────────────────────────────────────────


class ProjectNotFoundException(NotFoundException):
    def __init__(self) -> None:
        super().__init__(message="Project not found", code="PROJECT_NOT_FOUND")


class ProjectAlreadyExistsException(AppException):
    def __init__(self) -> None:
        super().__init__(message="Project already exists", code="PROJECT_ALREADY_EXISTS", status_code=409)


class ProjectAccessDeniedException(AuthorizationException):
    def __init__(self) -> None:
        super().__init__(message="Access denied to project", code="PROJECT_ACCESS_DENIED")


# ── Workflow Exceptions ───────────────────────────────────────────


class WorkflowNotFoundException(NotFoundException):
    def __init__(self) -> None:
        super().__init__(message="Workflow not found", code="WORKFLOW_NOT_FOUND")


class WorkflowValidationException(ValidationException):
    def __init__(self, detail: str = "") -> None:
        super().__init__(
            message=f"Workflow validation failed: {detail}" if detail else "Workflow validation failed",
            code="WORKFLOW_VALIDATION_ERROR",
        )


class WorkflowCircularDependencyException(ValidationException):
    def __init__(self) -> None:
        super().__init__(message="Circular dependency detected in workflow", code="WORKFLOW_CIRCULAR_DEPENDENCY")


class WorkflowExecutionException(WorkflowException):
    def __init__(self, detail: str = "") -> None:
        super().__init__(
            message=f"Workflow execution failed: {detail}" if detail else "Workflow execution failed",
            code="WORKFLOW_EXECUTION_ERROR",
        )


# ── Agent Exceptions ──────────────────────────────────────────────


class AgentNotFoundException(NotFoundException):
    def __init__(self) -> None:
        super().__init__(message="Agent not found", code="AGENT_NOT_FOUND")


class AgentExecutionException(AppException):
    def __init__(self, detail: str = "") -> None:
        super().__init__(
            message=f"Agent execution failed: {detail}" if detail else "Agent execution failed",
            code="AGENT_EXECUTION_ERROR",
            status_code=500,
        )


class AgentTimeoutException(AppException):
    def __init__(self) -> None:
        super().__init__(message="Agent execution timed out", code="AGENT_TIMEOUT", status_code=408)


class AgentToolException(AppException):
    def __init__(self, tool: str = "", detail: str = "") -> None:
        msg = f"Agent tool error ({tool}): {detail}" if tool else "Agent tool error"
        super().__init__(message=msg, code="AGENT_TOOL_ERROR")


# ── Plugin Exceptions ─────────────────────────────────────────────


class PluginNotFoundException(NotFoundException):
    def __init__(self) -> None:
        super().__init__(message="Plugin not found", code="PLUGIN_NOT_FOUND")


class PluginInstallException(PluginException):
    def __init__(self, detail: str = "") -> None:
        super().__init__(
            message=f"Plugin installation failed: {detail}" if detail else "Plugin installation failed",
            code="PLUGIN_INSTALL_ERROR",
        )


class PluginValidationException(ValidationException):
    def __init__(self, detail: str = "") -> None:
        super().__init__(
            message=f"Plugin validation failed: {detail}" if detail else "Plugin validation failed",
            code="PLUGIN_VALIDATION_ERROR",
        )


class PluginDependencyException(PluginException):
    def __init__(self, detail: str = "") -> None:
        super().__init__(
            message=f"Plugin dependency error: {detail}" if detail else "Plugin dependency error",
            code="PLUGIN_DEPENDENCY_ERROR",
        )


# ── Provider Exceptions ───────────────────────────────────────────


class ProviderNotFoundException(NotFoundException):
    def __init__(self) -> None:
        super().__init__(message="Provider not found", code="PROVIDER_NOT_FOUND")


class ProviderUnavailableException(ProviderException):
    def __init__(self, provider: str = "") -> None:
        super().__init__(
            message=f"Provider {provider} unavailable" if provider else "Provider unavailable",
            status_code=503,
            code="PROVIDER_UNAVAILABLE",
        )


class ProviderRateLimitException(ProviderException):
    def __init__(self, provider: str = "") -> None:
        super().__init__(
            message=f"Provider {provider} rate limit exceeded" if provider else "Provider rate limit exceeded",
            status_code=429,
            code="PROVIDER_RATE_LIMIT",
        )


# ── Knowledge Exceptions ──────────────────────────────────────────


class KnowledgeBaseNotFoundException(NotFoundException):
    def __init__(self) -> None:
        super().__init__(message="Knowledge base not found", code="KNOWLEDGE_BASE_NOT_FOUND")


class KnowledgeIndexException(AppException):
    def __init__(self, detail: str = "") -> None:
        super().__init__(
            message=f"Knowledge indexing failed: {detail}" if detail else "Knowledge indexing failed",
            code="KNOWLEDGE_INDEX_ERROR",
            status_code=500,
        )


# ── Runtime Exceptions ────────────────────────────────────────────


class SandboxCreationException(RuntimeException):
    def __init__(self) -> None:
        super().__init__(message="Failed to create sandbox", code="SANDBOX_CREATION_ERROR")


class ExecutionTimeoutException(RuntimeException):
    def __init__(self) -> None:
        super().__init__(message="Execution timed out", code="EXECUTION_TIMEOUT", status_code=408)


class ResourceLimitExceededException(RuntimeException):
    def __init__(self, resource: str = "") -> None:
        super().__init__(
            message=f"Resource limit exceeded: {resource}" if resource else "Resource limit exceeded",
            code="RESOURCE_LIMIT_EXCEEDED",
            status_code=429,
        )


# ── Database Exceptions ───────────────────────────────────────────


class RecordNotFoundException(DatabaseException):
    def __init__(self, model: str = "Record") -> None:
        super().__init__(message=f"{model} not found", code="RECORD_NOT_FOUND", status_code=404)


class DuplicateRecordException(DatabaseException):
    def __init__(self, model: str = "Record") -> None:
        super().__init__(message=f"Duplicate {model} found", code="DUPLICATE_RECORD", status_code=409)


# ── Storage Exceptions ────────────────────────────────────────────


class FileNotFoundError_(StorageException):
    def __init__(self, filename: str = "") -> None:
        super().__init__(
            message=f"File not found: {filename}" if filename else "File not found",
            code="FILE_NOT_FOUND",
            status_code=404,
        )


class FileTooLargeException(StorageException):
    def __init__(self, max_size: str = "") -> None:
        super().__init__(
            message=f"File too large (max: {max_size})" if max_size else "File too large",
            code="FILE_TOO_LARGE",
            status_code=413,
        )


class StorageQuotaExceededException(StorageException):
    def __init__(self) -> None:
        super().__init__(message="Storage quota exceeded", code="STORAGE_QUOTA_EXCEEDED", status_code=507)


# ── Deployment Exceptions ─────────────────────────────────────────


class DeploymentNotFoundException(NotFoundException):
    def __init__(self) -> None:
        super().__init__(message="Deployment not found", code="DEPLOYMENT_NOT_FOUND")


class DeploymentFailedException(AppException):
    def __init__(self, detail: str = "") -> None:
        super().__init__(
            message=f"Deployment failed: {detail}" if detail else "Deployment failed",
            code="DEPLOYMENT_FAILED",
            status_code=500,
        )


class BuildException(AppException):
    def __init__(self, detail: str = "") -> None:
        super().__init__(
            message=f"Build failed: {detail}" if detail else "Build failed",
            code="BUILD_ERROR",
            status_code=500,
        )


# ── Rate Limiting ─────────────────────────────────────────────────


class RateLimitException(AppException):
    def __init__(self, retry_after: int = 60) -> None:
        super().__init__(message="Rate limit exceeded", code="RATE_LIMIT", status_code=429)
        self.retry_after = retry_after


# ── Configuration Exceptions ──────────────────────────────────────


class MissingConfigException(ConfigurationException):
    def __init__(self, key: str = "") -> None:
        super().__init__(
            message=f"Missing configuration: {key}" if key else "Missing configuration",
            code="MISSING_CONFIG",
        )


class InvalidConfigException(ConfigurationException):
    def __init__(self, key: str = "", reason: str = "") -> None:
        msg = f"Invalid config for {key}: {reason}" if key else "Invalid configuration"
        super().__init__(message=msg, code="INVALID_CONFIG")
