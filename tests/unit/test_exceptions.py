"""Unit tests for backend.exceptions module."""

import pytest

from backend.exceptions import (
    AppException,
    AuthenticationException,
    AuthorizationException,
    BuildException,
    ConfigurationException,
    DatabaseException,
    DuplicateRecordException,
    ExecutionTimeoutException,
    InvalidConfigException,
    MissingConfigException,
    NotFoundException,
    PluginException,
    PluginNotFoundException,
    ProjectNotFoundException,
    ProviderException,
    ProviderNotFoundException,
    ProviderRateLimitException,
    ProviderUnavailableException,
    RateLimitException,
    RecordNotFoundException,
    RuntimeException,
    SecurityException,
    StorageException,
    UserAlreadyExistsException,
    UserNotFoundException,
    ValidationException,
    WorkflowNotFoundException,
)


class TestAppException:
    def test_base_exception(self):
        exc = AppException()
        assert exc.message == "An application error occurred"
        assert exc.code == "INTERNAL_ERROR"
        assert exc.status_code == 500
        assert exc.details == {}

    def test_custom_message(self):
        exc = AppException(message="Custom error", code="CUSTOM", status_code=400)
        assert exc.message == "Custom error"
        assert exc.code == "CUSTOM"
        assert exc.status_code == 400

    def test_with_details(self):
        exc = AppException(details={"field": "email"})
        assert exc.details == {"field": "email"}

    def test_is_exception(self):
        exc = AppException()
        assert isinstance(exc, Exception)


class TestNotFoundException:
    def test_default(self):
        exc = NotFoundException()
        assert exc.status_code == 404
        assert exc.code == "NOT_FOUND"

    def test_custom_message(self):
        exc = NotFoundException(message="Custom not found")
        assert exc.message == "Custom not found"

    def test_with_code_override(self):
        exc = NotFoundException(code="CUSTOM_NOT_FOUND")
        assert exc.code == "CUSTOM_NOT_FOUND"

    def test_is_app_exception(self):
        exc = NotFoundException()
        assert isinstance(exc, AppException)


class TestValidationException:
    def test_default(self):
        exc = ValidationException()
        assert exc.status_code == 422
        assert exc.code == "VALIDATION_ERROR"


class TestAuthenticationException:
    def test_default(self):
        exc = AuthenticationException()
        assert exc.status_code == 401
        assert exc.code == "AUTHENTICATION_ERROR"


class TestAuthorizationException:
    def test_default(self):
        exc = AuthorizationException()
        assert exc.status_code == 403
        assert exc.code == "AUTHORIZATION_ERROR"


class TestUserExceptions:
    def test_user_not_found(self):
        exc = UserNotFoundException()
        assert exc.status_code == 404
        assert "User not found" in exc.message
        assert exc.code == "USER_NOT_FOUND"

    def test_user_not_found_custom_identifier(self):
        exc = UserNotFoundException(identifier="Admin")
        assert "Admin not found" in exc.message

    def test_user_already_exists(self):
        exc = UserAlreadyExistsException(field="email")
        assert exc.status_code == 409
        assert "email" in exc.message

    def test_user_already_exists_default(self):
        exc = UserAlreadyExistsException()
        assert "email" in exc.message


class TestProjectExceptions:
    def test_project_not_found(self):
        exc = ProjectNotFoundException()
        assert exc.status_code == 404
        assert exc.code == "PROJECT_NOT_FOUND"


class TestWorkflowExceptions:
    def test_workflow_not_found(self):
        exc = WorkflowNotFoundException()
        assert exc.status_code == 404
        assert exc.code == "WORKFLOW_NOT_FOUND"


class TestPluginExceptions:
    def test_plugin_not_found(self):
        exc = PluginNotFoundException()
        assert exc.status_code == 404
        assert exc.code == "PLUGIN_NOT_FOUND"


class TestProviderExceptions:
    def test_provider_not_found(self):
        exc = ProviderNotFoundException()
        assert exc.status_code == 404

    def test_provider_unavailable(self):
        exc = ProviderUnavailableException(provider="openai")
        assert exc.status_code == 503
        assert "openai" in exc.message

    def test_provider_rate_limit(self):
        exc = ProviderRateLimitException(provider="anthropic")
        assert exc.status_code == 429
        assert "anthropic" in exc.message


class TestDatabaseExceptions:
    def test_record_not_found(self):
        exc = RecordNotFoundException(model="User")
        assert exc.status_code == 404
        assert "User" in exc.message

    def test_duplicate_record(self):
        exc = DuplicateRecordException(model="Project")
        assert exc.status_code == 409


class TestRuntimeExceptions:
    def test_execution_timeout(self):
        exc = ExecutionTimeoutException()
        assert exc.status_code == 408

    def test_rate_limit(self):
        exc = RateLimitException(retry_after=120)
        assert exc.status_code == 429
        assert exc.retry_after == 120


class TestConfigurationExceptions:
    def test_missing_config(self):
        exc = MissingConfigException(key="DATABASE_URL")
        assert "DATABASE_URL" in exc.message

    def test_invalid_config(self):
        exc = InvalidConfigException(key="PORT", reason="not a number")
        assert "PORT" in exc.message
        assert "not a number" in exc.message


class TestBuildException:
    def test_build_failed(self):
        exc = BuildException(detail="Compilation error")
        assert exc.status_code == 500
        assert "Compilation error" in exc.message

    def test_build_failed_default(self):
        exc = BuildException()
        assert exc.message == "Build failed"
