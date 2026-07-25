from __future__ import annotations

import uuid
from typing import Any

from ..projects.repository import ProjectMemberRepository, ProjectRepository
from .roles import get_default_role, get_role


class PermissionResolver:
    def __init__(
        self,
        project_repo: ProjectRepository,
        member_repo: ProjectMemberRepository,
    ):
        self.project_repo = project_repo
        self.member_repo = member_repo

    async def get_user_permissions(
        self, user_id: uuid.UUID, context: dict[str, Any] | None = None
    ) -> list[str]:
        context = context or {}
        permissions: list[str] = []

        explicit_roles = context.get("roles", [])
        for role_name in explicit_roles:
            role = get_role(role_name)
            if role:
                permissions.extend(role.permissions)

        if not permissions:
            default_role = get_default_role()
            permissions = list(default_role.permissions)

        return list(set(permissions))

    async def resolve_project_permissions(
        self, user_id: uuid.UUID, project_id: uuid.UUID
    ) -> list[str]:
        permissions: list[str] = []
        member = await self.member_repo.get_member(project_id, user_id)
        if member:
            role = get_role(member.role)
            if not role:
                role_name = member.role
                role = get_role(role_name)
            if role:
                permissions = list(role.permissions)
        else:
            project = await self.project_repo.get_by_id(project_id)
            if project and project.is_public:
                default = get_default_role()
                permissions = [p for p in default.permissions if p.startswith("project:")]

        return permissions

    async def resolve_org_permissions(
        self, user_id: uuid.UUID, org_id: uuid.UUID
    ) -> list[str]:
        permissions: list[str] = []
        return permissions

    async def has_permission(
        self,
        user_id: uuid.UUID,
        permission: str,
        resource_type: str,
        resource_id: uuid.UUID | None = None,
    ) -> bool:
        context_permissions = await self.get_user_permissions(user_id)

        if permission in context_permissions:
            return True

        if resource_type == "project" and resource_id:
            project_perms = await self.resolve_project_permissions(user_id, resource_id)
            if permission in project_perms:
                return True

        return False