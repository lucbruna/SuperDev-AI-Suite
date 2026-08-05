"""AIOS Kernel Security — local access-control checks.

The kernel security layer evaluates ``(actor, action, resource)``
against a simple policy table before sensitive operations. The full
RBAC lives in ``services.authorization``; this class guards the kernel
itself (boot, shutdown, component attachment, service registration).
"""

from __future__ import annotations

from typing import Any

# Built-in principals
ACTOR_SYSTEM = "system"
ACTOR_ADMIN = "admin"
ACTOR_SERVICE = "service"
ACTOR_AGENT = "agent"
ACTOR_USER = "user"

ALLOWED_ACTIONS = frozenset(
    {"boot", "shutdown", "attach", "register_service", "register_module", "dispatch"}
)


class KernelSecurityError(PermissionError):
    """Raised when a kernel-level access control check fails."""


class KernelSecurity:
    """Policy evaluator for kernel operations."""

    def __init__(self) -> None:
        # actor -> allowed actions (empty set means no kernel-level access)
        self._policies: dict[str, set[str]] = {
            ACTOR_SYSTEM: set(ALLOWED_ACTIONS),
            ACTOR_ADMIN: set(ALLOWED_ACTIONS),
            ACTOR_SERVICE: {"attach", "register_service", "dispatch"},
            ACTOR_AGENT: {"dispatch"},
            ACTOR_USER: set(),
        }

    def grant(self, actor: str, *actions: str) -> "KernelSecurity":
        self._policies.setdefault(actor, set()).update(actions)
        return self

    def revoke(self, actor: str, *actions: str) -> "KernelSecurity":
        self._policies.get(actor, set()).difference_update(actions)
        return self

    def check(self, actor: str, action: str, resource: str | None = None) -> bool:
        allowed = self._policies.get(actor, set())
        ok = action in allowed
        if resource is not None and ok:
            # Convention: "<resource>.*" grants all actions on the resource.
            wildcard = f"{resource}.*"
            ok = wildcard in allowed or action in allowed
        return ok

    def assert_allowed(self, actor: str, action: str, resource: str | None = None) -> None:
        if not self.check(actor, action, resource):
            raise KernelSecurityError(
                f"actor={actor!r} not allowed action={action!r} on resource={resource!r}"
            )

    def snapshot(self) -> dict[str, Any]:
        return {
            actor: sorted(actions)
            for actor, actions in sorted(self._policies.items())
            if actions
        }
