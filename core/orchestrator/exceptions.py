"""Exception hierarchy for the SuperDev System Orchestrator.

Every exception raised within the orchestrator and its sub-components
inherits from OrchestratorError, enabling clean error handling at the
top level without losing specificity.
"""

from __future__ import annotations


class OrchestratorError(Exception):
    """Base exception for all orchestrator errors."""
    def __init__(self, message: str = "", service: str = "",
                 recoverable: bool = False) -> None:
        self.service = service
        self.recoverable = recoverable
        super().__init__(message)


# ─── Boot / Startup ──────────────────────────────────────────────────────────

class BootError(OrchestratorError):
    """Raised when the system fails to boot a service during startup."""
    def __init__(self, service: str, message: str = "") -> None:
        super().__init__(
            message or f"Failed to boot service '{service}'",
            service=service,
            recoverable=False,
        )


class BootTimeoutError(BootError):
    """Raised when a service takes too long to initialize."""
    def __init__(self, service: str, timeout: float) -> None:
        super().__init__(
            service=service,
            message=f"Service '{service}' did not start within {timeout}s",
        )


# ─── Service Registry ────────────────────────────────────────────────────────

class ServiceNotFoundError(OrchestratorError):
    """Raised when a requested service is not registered."""
    def __init__(self, service: str) -> None:
        super().__init__(
            message=f"Service '{service}' not found in registry",
            service=service,
            recoverable=True,
        )


class ServiceAlreadyRegisteredError(OrchestratorError):
    """Raised when trying to register a service that already exists."""
    def __init__(self, service: str) -> None:
        super().__init__(
            message=f"Service '{service}' is already registered",
            service=service,
        )


class ServiceDependencyError(OrchestratorError):
    """Raised when a service's dependencies are unmet."""
    def __init__(self, service: str, missing_deps: list[str]) -> None:
        deps_str = ", ".join(missing_deps)
        super().__init__(
            message=f"Service '{service}' has unmet dependencies: {deps_str}",
            service=service,
            recoverable=True,
        )


# ─── Event Bus ───────────────────────────────────────────────────────────────

class EventBusError(OrchestratorError):
    """Base for event bus errors."""
    def __init__(self, message: str = "") -> None:
        super().__init__(message=message, recoverable=True)


class EventDeliveryError(EventBusError):
    """Raised when an event cannot be delivered to a subscriber."""
    def __init__(self, event_type: str, subscriber: str, reason: str = "") -> None:
        super().__init__(
            message=f"Failed to deliver event '{event_type}' to '{subscriber}': {reason}",
        )


# ─── State Management ────────────────────────────────────────────────────────

class StateError(OrchestratorError):
    """Base for state management errors."""
    def __init__(self, message: str = "") -> None:
        super().__init__(message=message, recoverable=True)


class StatePersistenceError(StateError):
    """Raised when state cannot be persisted or loaded."""
    def __init__(self, path: str, reason: str = "") -> None:
        super().__init__(
            message=f"Failed to persist/load state at '{path}': {reason}",
        )


# ─── Recovery ────────────────────────────────────────────────────────────────

class RecoveryError(OrchestratorError):
    """Raised when a recovery operation fails."""
    def __init__(self, service: str, attempts: int,
                 last_error: str = "") -> None:
        super().__init__(
            message=f"Recovery failed for '{service}' after {attempts} attempts: {last_error}",
            service=service,
            recoverable=False,
        )


# ─── Shutdown ────────────────────────────────────────────────────────────────

class ShutdownError(OrchestratorError):
    """Raised when a graceful shutdown fails."""
    def __init__(self, service: str, reason: str = "") -> None:
        super().__init__(
            message=f"Failed to shut down service '{service}': {reason}",
            service=service,
        )


class ShutdownTimeoutError(ShutdownError):
    """Raised when a service takes too long to shut down."""
    def __init__(self, service: str, timeout: float) -> None:
        super().__init__(
            service=service,
            reason=f"did not stop within {timeout}s",
        )


# ─── Metrics ─────────────────────────────────────────────────────────────────

class MetricsError(OrchestratorError):
    """Raised when metrics collection or export fails."""
    def __init__(self, message: str = "") -> None:
        super().__init__(message=message, recoverable=True)
