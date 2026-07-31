from __future__ import annotations

import uuid
from collections.abc import Callable
from functools import wraps
from typing import Any

from fastapi import HTTPException, status

from ..projects.repository import ProjectMemberRepository, ProjectRepository
from .cache import PermissionCache
from .policy import PolicyEngine
from .resolver import PermissionResolver


class PermissionEngine:
    def __init__(self, session):
        self.session = session
        self.project_repo = ProjectRepository(session)
        self.member_repo = ProjectMemberRepository(session)
        self.resolver = PermissionResolver(self.project_repo, self.member_repo)
        self.policy = PolicyEngine()
        self.cache = PermissionCache()

    async def check(
        self,
        user_id: uuid.UUID,
        permission: str,
        resource_type: str,
        resource_id: uuid.UUID | None = None,
    ) -> bool:
        cached = self.cache.get_cached_permissions(user_id)
        if cached is not None:
            if permission in cached:
                return True

        result = await self.resolver.has_permission(user_id, permission, resource_type, resource_id)
        if result:
            user_perms = await self.resolver.get_user_permissions(user_id)
            self.cache.set_cached_permissions(user_id, user_perms)

        return result

    async def get_effective_permissions(self, user_id: uuid.UUID) -> list[str]:
        cached = self.cache.get_cached_permissions(user_id)
        if cached is not None:
            return cached

        user_perms = await self.resolver.get_user_permissions(user_id)
        self.cache.set_cached_permissions(user_id, user_perms)
        return user_perms


def require(permission: str, resource_type: str) -> Callable:
    def decorator(endpoint: Callable) -> Callable:
        @wraps(endpoint)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            current_user = kwargs.get("current_user") or kwargs.get("user")
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )

            session = kwargs.get("session")
            if not session:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Database session not available",
                )

            engine = PermissionEngine(session)
            user_id = current_user.get("id")
            resource_id = kwargs.get("project_id") or kwargs.get(f"{resource_type}_id")

            has_perm = await engine.check(
                user_id=user_id,
                permission=permission,
                resource_type=resource_type,
                resource_id=resource_id,
            )
            if not has_perm:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing required permission: {permission}",
                )

            return await endpoint(*args, **kwargs)

        return wrapper

    return decorator
