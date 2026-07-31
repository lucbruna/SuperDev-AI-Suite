"""RBAC module — re-exports from the canonical backend.auth.rbac implementation.

The canonical RBAC module lives in backend.auth.rbac. This file exists for
backward compatibility only.
"""

from backend.auth.rbac import (  # noqa: F401
    Action,
    PermissionChecker,
    Resource,
    RoleName,
    assign_role,
    ensure_system_roles,
    get_user_permissions,
    require_permission,
)

# Backward-compatible alias: RBACEngine → PermissionChecker
RBACEngine = PermissionChecker

__all__ = [
    "Action",
    "PermissionChecker",
    "RBACEngine",
    "Resource",
    "RoleName",
    "assign_role",
    "ensure_system_roles",
    "get_user_permissions",
    "require_permission",
]
