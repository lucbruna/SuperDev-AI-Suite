from __future__ import annotations

from backend.exceptions import (
    AppException,
    AuthenticationException,
    AuthorizationException,
    ConfigurationException,
    DatabaseException,
    NotFoundException,
    PluginException,
    ProviderException,
    RuntimeException,
    SecurityException,
    StorageException,
    ValidationException,
    WorkflowException,
)


class TestAppException:
    def test_default_values(self) -> None:
        exc = AppException()
        assert exc.message == "An application error occurred"
        assert exc.code == "INTERNAL_ERROR"
        assert exc.status_code == 500
        assert exc.details == {}

    def test_custom_values(self) -> None:
        exc = AppException(
            message="Custom error",
            code="CUSTOM_CODE",
            status_code=400,
            details={"field": "value"},
        )
        assert exc.message == "Custom error"
        assert exc.code == "CUSTOM_CODE"
        assert exc.status_code == 400
        assert exc.details == {"field": "value"}

    def test_inherits_from_exception(self) -> None:
        exc = AppException()
        assert isinstance(exc, Exception)

    def test_str_representation(self) -> None:
        exc = AppException(message="Something went wrong")
        assert str(exc) == "Something went wrong"


class TestNotFoundException:
    def test_inheritance(self) -> None:
        exc = NotFoundException()
        assert isinstance(exc, AppException)

    def test_default_properties(self) -> None:
        exc = NotFoundException()
        assert exc.message == "Resource not found"
        assert exc.code == "NOT_FOUND"
        assert exc.status_code == 404

    def test_custom_message(self) -> None:
        exc = NotFoundException(message="User not found")
        assert exc.message == "User not found"


class TestValidationException:
    def test_inheritance(self) -> None:
        exc = ValidationException()
        assert isinstance(exc, AppException)

    def test_default_properties(self) -> None:
        exc = ValidationException()
        assert exc.message == "Validation failed"
        assert exc.code == "VALIDATION_ERROR"
        assert exc.status_code == 422


class TestAuthenticationException:
    def test_inheritance(self) -> None:
        exc = AuthenticationException()
        assert isinstance(exc, AppException)

    def test_default_properties(self) -> None:
        exc = AuthenticationException()
        assert exc.message == "Authentication failed"
        assert exc.code == "AUTHENTICATION_ERROR"
        assert exc.status_code == 401


class TestAuthorizationException:
    def test_inheritance(self) -> None:
        exc = AuthorizationException()
        assert isinstance(exc, AppException)

    def test_default_properties(self) -> None:
        exc = AuthorizationException()
        assert exc.message == "Access denied"
        assert exc.code == "AUTHORIZATION_ERROR"
        assert exc.status_code == 403


class TestConfigurationException:
    def test_inheritance(self) -> None:
        exc = ConfigurationException()
        assert isinstance(exc, AppException)

    def test_default_properties(self) -> None:
        exc = ConfigurationException()
        assert exc.message == "Configuration error"
        assert exc.code == "CONFIGURATION_ERROR"
        assert exc.status_code == 500


class TestPluginException:
    def test_inheritance(self) -> None:
        exc = PluginException()
        assert isinstance(exc, AppException)

    def test_default_properties(self) -> None:
        exc = PluginException()
        assert exc.message == "Plugin error"
        assert exc.code == "PLUGIN_ERROR"
        assert exc.status_code == 500


class TestProviderException:
    def test_inheritance(self) -> None:
        exc = ProviderException()
        assert isinstance(exc, AppException)

    def test_default_properties(self) -> None:
        exc = ProviderException()
        assert exc.message == "Provider error"
        assert exc.code == "PROVIDER_ERROR"
        assert exc.status_code == 502


class TestWorkflowException:
    def test_inheritance(self) -> None:
        exc = WorkflowException()
        assert isinstance(exc, AppException)

    def test_default_properties(self) -> None:
        exc = WorkflowException()
        assert exc.message == "Workflow error"
        assert exc.code == "WORKFLOW_ERROR"
        assert exc.status_code == 500


class TestRuntimeException:
    def test_inheritance(self) -> None:
        exc = RuntimeException()
        assert isinstance(exc, AppException)

    def test_default_properties(self) -> None:
        exc = RuntimeException()
        assert exc.message == "Runtime error"
        assert exc.code == "RUNTIME_ERROR"
        assert exc.status_code == 500


class TestDatabaseException:
    def test_inheritance(self) -> None:
        exc = DatabaseException()
        assert isinstance(exc, AppException)

    def test_default_properties(self) -> None:
        exc = DatabaseException()
        assert exc.message == "Database error"
        assert exc.code == "DATABASE_ERROR"
        assert exc.status_code == 500


class TestSecurityException:
    def test_inheritance(self) -> None:
        exc = SecurityException()
        assert isinstance(exc, AppException)

    def test_default_properties(self) -> None:
        exc = SecurityException()
        assert exc.message == "Security violation"
        assert exc.code == "SECURITY_ERROR"
        assert exc.status_code == 403


class TestStorageException:
    def test_inheritance(self) -> None:
        exc = StorageException()
        assert isinstance(exc, AppException)

    def test_default_properties(self) -> None:
        exc = StorageException()
        assert exc.message == "Storage error"
        assert exc.code == "STORAGE_ERROR"
        assert exc.status_code == 500


class TestExceptionDetails:
    def test_all_exceptions_pass_details(self) -> None:
        details = {"reason": "test"}
        exc = NotFoundException(details=details)
        assert exc.details == details

    def test_exception_custom_details_merged(self) -> None:
        exc = ValidationException(message="Custom", details={"field": "email"})
        assert exc.message == "Custom"
        assert exc.details == {"field": "email"}