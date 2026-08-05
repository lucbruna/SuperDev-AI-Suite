"""Auth dependencies for the module API (graceful degradation).

The module prefers the platform's ``get_current_user`` when available, but
falls back to an anonymous user so the router stays importable in test and
standalone contexts.
"""
from __future__ import annotations

from typing import Any

_ANONYMOUS: dict[str, Any] = {"sub": None, "anonymous": True}


async def get_optional_user() -> dict[str, Any]:
    """Return the authenticated user dict, or an anonymous marker.

    When the platform auth is available this resolves the token; otherwise it
    returns the anonymous marker so every endpoint keeps working.
    """
    try:
        from backend.dependencies import get_current_user

        return await get_current_user()
    except Exception:
        return dict(_ANONYMOUS)


async def get_required_user() -> dict[str, Any]:
    """Require authentication; raises when auth is unavailable."""
    user = await get_optional_user()
    if user.get("anonymous"):
        raise PermissionError("Authentication required")
    return user


def has_capability(user: dict[str, Any], capability: str) -> bool:
    """Coarse capability check over the user payload (best effort)."""
    if user.get("anonymous"):
        return False
    roles = user.get("roles") or []
    capabilities = user.get("capabilities") or []
    if isinstance(roles, str):
        roles = [roles]
    return capability in capabilities or "admin" in roles
