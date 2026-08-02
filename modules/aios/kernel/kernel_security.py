"""Kernel security — component/action access control list."""
from __future__ import annotations
from typing import Any


class KernelPermissionDeniedError(PermissionError):
    def __init__(self, component: str, action: str) -> None:
        self.component = component
        self.action = action
        super().__init__(f"kernel permission denied: {component}:{action}")


class KernelSecurity:
    """ACL over ``component:action`` pairs, granted explicitly."""

    def __init__(self) -> None:
        self._grants: dict[str, set[str]] = {}

    def grant(self, component: str, *actions: str) -> None:
        self._grants.setdefault(component, set()).update(actions)

    def revoke(self, component: str, *actions: str) -> None:
        self._grants.get(component, set()).difference_update(actions)

    def allow(self, component: str, action: str) -> bool:
        return action in self._grants.get(component, set())

    def require(self, component: str, action: str) -> None:
        if not self.allow(component, action):
            raise KernelPermissionDeniedError(component, action)

    def snapshot(self) -> dict[str, Any]:
        return {
            "grants": {c: sorted(a) for c, a in self._grants.items()},
            "total": sum(len(a) for a in self._grants.values()),
        }


_kernel_security: KernelSecurity | None = None


def get_kernel_security() -> KernelSecurity:
    global _kernel_security
    if _kernel_security is None:
        _kernel_security = KernelSecurity()
    return _kernel_security
