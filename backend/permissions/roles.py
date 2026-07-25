from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from .permissions import (
    AdminPermissions,
    AgentPermissions,
    OrgPermissions,
    PluginPermissions,
    ProjectPermissions,
    UserPermissions,
    WorkflowPermissions,
    WorkspacePermissions,
)


class PredefinedRole(StrEnum):
    ADMIN = "admin"
    OWNER = "owner"
    DEVELOPER = "developer"
    VIEWER = "viewer"


@dataclass
class Role:
    name: str
    description: str
    permissions: list[str] = field(default_factory=list)

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions

    def add_permission(self, permission: str) -> None:
        if permission not in self.permissions:
            self.permissions.append(permission)

    def remove_permission(self, permission: str) -> None:
        if permission in self.permissions:
            self.permissions.remove(permission)


PREDEFINED_ROLES: dict[str, Role] = {
    PredefinedRole.ADMIN.value: Role(
        name="admin",
        description="Full system access with all permissions",
        permissions=[
            ProjectPermissions.READ,
            ProjectPermissions.WRITE,
            ProjectPermissions.DELETE,
            ProjectPermissions.ADMIN,
            OrgPermissions.READ,
            OrgPermissions.WRITE,
            OrgPermissions.ADMIN,
            UserPermissions.READ,
            UserPermissions.WRITE,
            WorkspacePermissions.READ,
            WorkspacePermissions.WRITE,
            AgentPermissions.READ,
            AgentPermissions.WRITE,
            AgentPermissions.EXECUTE,
            WorkflowPermissions.READ,
            WorkflowPermissions.WRITE,
            WorkflowPermissions.EXECUTE,
            PluginPermissions.INSTALL,
            AdminPermissions.ACCESS,
        ],
    ),
    PredefinedRole.OWNER.value: Role(
        name="owner",
        description="Organization and project admin access",
        permissions=[
            ProjectPermissions.READ,
            ProjectPermissions.WRITE,
            ProjectPermissions.DELETE,
            ProjectPermissions.ADMIN,
            OrgPermissions.READ,
            OrgPermissions.WRITE,
            OrgPermissions.ADMIN,
            UserPermissions.READ,
            UserPermissions.WRITE,
            WorkspacePermissions.READ,
            WorkspacePermissions.WRITE,
            AgentPermissions.READ,
            AgentPermissions.WRITE,
            AgentPermissions.EXECUTE,
            WorkflowPermissions.READ,
            WorkflowPermissions.WRITE,
            WorkflowPermissions.EXECUTE,
            PluginPermissions.INSTALL,
        ],
    ),
    PredefinedRole.DEVELOPER.value: Role(
        name="developer",
        description="Read/write access to most resources, can execute agents and workflows",
        permissions=[
            ProjectPermissions.READ,
            ProjectPermissions.WRITE,
            OrgPermissions.READ,
            UserPermissions.READ,
            UserPermissions.WRITE,
            WorkspacePermissions.READ,
            WorkspacePermissions.WRITE,
            AgentPermissions.READ,
            AgentPermissions.WRITE,
            AgentPermissions.EXECUTE,
            WorkflowPermissions.READ,
            WorkflowPermissions.WRITE,
            WorkflowPermissions.EXECUTE,
        ],
    ),
    PredefinedRole.VIEWER.value: Role(
        name="viewer",
        description="Read-only access to most resources",
        permissions=[
            ProjectPermissions.READ,
            OrgPermissions.READ,
            UserPermissions.READ,
            WorkspacePermissions.READ,
            AgentPermissions.READ,
            WorkflowPermissions.READ,
        ],
    ),
}


def get_role(name: str) -> Role | None:
    return PREDEFINED_ROLES.get(name)


def get_default_role() -> Role:
    return PREDEFINED_ROLES[PredefinedRole.VIEWER.value]


def create_custom_role(name: str, permissions: list[str]) -> Role:
    return Role(
        name=name,
        description=f"Custom role: {name}",
        permissions=permissions,
    )