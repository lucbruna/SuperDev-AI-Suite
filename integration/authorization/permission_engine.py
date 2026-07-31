from __future__ import annotations

import logging
from typing import Any

from .access_policy import AccessPolicy
from .validation import PermissionValidator


class PermissionEngine:
    """Facade for authorization: role mapping, scopes, policies, and validation."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.integration.authorization")
        self.validator = PermissionValidator()
        # Share the validator's mappers so operations are consistent.
        self.roles = self.validator.roles
        self.scopes = self.validator.scopes
        self.policies = AccessPolicy()

    def define_role(self, role: str, permissions: list[str]) -> None:
        self.roles.define_role(role, permissions)

    def assign(self, user: str, role: str) -> None:
        self.roles.assign(user, role)

    def enforce(self, user: str, permission: str,
                granted_scopes: list[str] | None = None) -> None:
        self.validator.enforce_permission(user, permission)
        if granted_scopes:
            self.scopes.require(granted_scopes, permission)

    def check(self, user: str, permission: str,
              granted_scopes: list[str] | None = None) -> bool:
        return self.validator.validate(user, permission, granted_scopes)

    def evaluate_policy(self, action: str, resource: str,
                        context: dict[str, Any] | None = None) -> bool:
        return self.policies.evaluate(action, resource, context)

    def stats(self) -> dict[str, int]:
        return self.validator.snapshot()


# Backwards-compatible alias for the facade.
AuthorizationEngine = PermissionEngine
