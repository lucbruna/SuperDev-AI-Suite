from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .ai_types import PermissionLevel


class AIPermissions:
    """Permissions management for AI operations."""

    def __init__(self):
        self._permissions: dict[str, set[str]] = {}
        self._role_permissions: dict[str, set[str]] = {
            "admin": {
                "engine.*", "provider.*", "agent.*", "tool.*",
                "model.*", "session.*", "runtime.*", "metrics.*",
                "config.*", "logs.*",
            },
            "user": {
                "agent.execute", "agent.list", "tool.execute", "tool.list",
                "model.list", "session.create", "session.list",
                "chat.*", "embeddings.*",
            },
            "viewer": {
                "agent.list", "tool.list", "model.list", "session.list",
            },
        }
        self._cache: dict[str, bool] = {}

    def check_permission(self, user_id: str, action: str, role: str | None = None) -> bool:
        """Check if a user has permission for an action."""
        cache_key = f"{user_id}:{action}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        effective_role: str = role or "user"

        # Check user-specific permissions first
        user_perms = self._permissions.get(user_id, set())
        if self._match_permission(user_perms, action):
            self._cache[cache_key] = True
            return True

        # Check role-based permissions
        role_perms = self._role_permissions.get(effective_role, set())
        result = self._match_permission(role_perms, action)
        self._cache[cache_key] = result
        return result

    def grant_permission(self, user_id: str, action: str) -> None:
        """Grant a specific permission to a user."""
        if user_id not in self._permissions:
            self._permissions[user_id] = set()
        self._permissions[user_id].add(action)
        self._invalidate_cache(user_id)

    def revoke_permission(self, user_id: str, action: str) -> None:
        """Revoke a specific permission from a user."""
        if user_id in self._permissions:
            self._permissions[user_id].discard(action)
            self._invalidate_cache(user_id)

    def set_role_permissions(self, role: str, permissions: set[str]) -> None:
        """Set permissions for a role."""
        self._role_permissions[role] = permissions
        self._cache.clear()

    def get_user_permissions(self, user_id: str) -> set[str]:
        """Get all permissions for a user."""
        return self._permissions.get(user_id, set())

    def get_role_permissions(self, role: str) -> set[str]:
        """Get permissions for a role."""
        return self._role_permissions.get(role, set())

    def clear_cache(self) -> None:
        """Clear the permission cache."""
        self._cache.clear()

    def _match_permission(self, permissions: set[str], action: str) -> bool:
        """Check if an action matches a set of permission patterns."""
        for perm in permissions:
            if perm.endswith(".*"):
                prefix = perm[:-2]
                if action.startswith(prefix):
                    return True
            elif perm == action:
                return True
        return False

    def _invalidate_cache(self, user_id: str) -> None:
        """Invalidate cache entries for a user."""
        keys_to_remove = [k for k in self._cache if k.startswith(f"{user_id}:")]
        for key in keys_to_remove:
            del self._cache[key]

    def health(self) -> dict[str, Any]:
        """Get permissions subsystem health."""
        return {
            "status": "healthy",
            "users_with_permissions": len(self._permissions),
            "roles": list(self._role_permissions.keys()),
            "cache_size": len(self._cache),
            "timestamp": datetime.now(UTC).isoformat(),
        }
