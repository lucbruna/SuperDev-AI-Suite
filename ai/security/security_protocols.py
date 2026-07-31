"""Security protocols for cross-system security operations."""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from typing import Protocol, runtime_checkable


@runtime_checkable
class Securable(Protocol):
    def secure(self) -> Dict[str, Any]: ...

    def is_secure(self) -> bool: ...


@runtime_checkable
class Authenticatable(Protocol):
    def authenticate(self, credentials: Dict[str, Any]) -> bool: ...

    def deauthenticate(self) -> None: ...


@runtime_checkable
class Auditable(Protocol):
    def audit_log(self, action: str, details: Dict[str, Any]) -> None: ...

    def get_audit_trail(self) -> List[Dict[str, Any]]: ...


@runtime_checkable
class Compliant(Protocol):
    def check_compliance(self, standard: str) -> bool: ...

    def get_compliance_report(self, standard: str) -> Dict[str, Any]: ...


class SecurityProtocol:
    """Protocol definitions for security contracts across the platform."""

    REQUIRED_SECURITY_LEVELS = {
        "data_access": "high",
        "agent_execution": "critical",
        "api_call": "medium",
        "user_login": "high",
        "config_change": "critical",
        "secret_access": "critical",
    }

    @classmethod
    def required_level(cls, operation: str) -> str:
        return cls.REQUIRED_SECURITY_LEVELS.get(operation, "medium")
