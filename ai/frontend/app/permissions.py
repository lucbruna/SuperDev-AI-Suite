"""
Frontend Permissions System
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Permission(Enum):
    """System permissions."""
    # Dashboard
    VIEW_DASHBOARD = "view_dashboard"
    EDIT_DASHBOARD = "edit_dashboard"
    DELETE_DASHBOARD = "delete_dashboard"

    # Projects
    VIEW_PROJECTS = "view_projects"
    CREATE_PROJECT = "create_project"
    EDIT_PROJECT = "edit_project"
    DELETE_PROJECT = "delete_project"
    MANAGE_PROJECT_MEMBERS = "manage_project_members"

    # Agents
    VIEW_AGENTS = "view_agents"
    CREATE_AGENT = "create_agent"
    EDIT_AGENT = "edit_agent"
    DELETE_AGENT = "delete_agent"
    EXECUTE_AGENT = "execute_agent"

    # Code Editor
    VIEW_CODE = "view_code"
    EDIT_CODE = "edit_code"
    EXECUTE_CODE = "execute_code"

    # Automation
    VIEW_AUTOMATION = "view_automation"
    CREATE_AUTOMATION = "create_automation"
    EDIT_AUTOMATION = "edit_automation"
    DELETE_AUTOMATION = "delete_automation"

    # Analytics
    VIEW_ANALYTICS = "view_analytics"
    EXPORT_ANALYTICS = "export_analytics"

    # Administration
    VIEW_ADMIN = "view_admin"
    MANAGE_USERS = "manage_users"
    MANAGE_TENANTS = "manage_tenants"
    MANAGE_ROLES = "manage_roles"
    VIEW_AUDIT_LOG = "view_audit_log"

    # Billing
    VIEW_BILLING = "view_billing"
    MANAGE_BILLING = "manage_billing"

    # Settings
    VIEW_SETTINGS = "view_settings"
    EDIT_SETTINGS = "edit_settings"

    # Real-time
    VIEW_REALTIME = "view_realtime"
    MANAGE_REALTIME = "manage_realtime"


class Role(Enum):
    """User roles."""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MANAGER = "manager"
    DEVELOPER = "developer"
    VIEWER = "viewer"
    GUEST = "guest"


@dataclass
class RolePermissions:
    """Role to permissions mapping."""
    role: Role
    permissions: set[Permission] = field(default_factory=set)

    @classmethod
    def default(cls, role: Role) -> "RolePermissions":
        """Get default permissions for a role."""
        permissions = {
            Role.SUPER_ADMIN: set(Permission),  # All permissions
            Role.ADMIN: {
                Permission.VIEW_DASHBOARD,
                Permission.EDIT_DASHBOARD,
                Permission.VIEW_PROJECTS,
                Permission.CREATE_PROJECT,
                Permission.EDIT_PROJECT,
                Permission.DELETE_PROJECT,
                Permission.MANAGE_PROJECT_MEMBERS,
                Permission.VIEW_AGENTS,
                Permission.CREATE_AGENT,
                Permission.EDIT_AGENT,
                Permission.DELETE_AGENT,
                Permission.EXECUTE_AGENT,
                Permission.VIEW_CODE,
                Permission.EDIT_CODE,
                Permission.EXECUTE_CODE,
                Permission.VIEW_AUTOMATION,
                Permission.CREATE_AUTOMATION,
                Permission.EDIT_AUTOMATION,
                Permission.DELETE_AUTOMATION,
                Permission.VIEW_ANALYTICS,
                Permission.EXPORT_ANALYTICS,
                Permission.VIEW_ADMIN,
                Permission.MANAGE_USERS,
                Permission.MANAGE_TENANTS,
                Permission.MANAGE_ROLES,
                Permission.VIEW_AUDIT_LOG,
                Permission.VIEW_BILLING,
                Permission.MANAGE_BILLING,
                Permission.VIEW_SETTINGS,
                Permission.EDIT_SETTINGS,
                Permission.VIEW_REALTIME,
                Permission.MANAGE_REALTIME,
            },
            Role.MANAGER: {
                Permission.VIEW_DASHBOARD,
                Permission.EDIT_DASHBOARD,
                Permission.VIEW_PROJECTS,
                Permission.CREATE_PROJECT,
                Permission.EDIT_PROJECT,
                Permission.VIEW_AGENTS,
                Permission.CREATE_AGENT,
                Permission.EDIT_AGENT,
                Permission.EXECUTE_AGENT,
                Permission.VIEW_CODE,
                Permission.EDIT_CODE,
                Permission.VIEW_AUTOMATION,
                Permission.CREATE_AUTOMATION,
                Permission.EDIT_AUTOMATION,
                Permission.VIEW_ANALYTICS,
                Permission.EXPORT_ANALYTICS,
                Permission.VIEW_BILLING,
                Permission.VIEW_SETTINGS,
                Permission.VIEW_REALTIME,
            },
            Role.DEVELOPER: {
                Permission.VIEW_DASHBOARD,
                Permission.VIEW_PROJECTS,
                Permission.CREATE_PROJECT,
                Permission.EDIT_PROJECT,
                Permission.VIEW_AGENTS,
                Permission.CREATE_AGENT,
                Permission.EXECUTE_AGENT,
                Permission.VIEW_CODE,
                Permission.EDIT_CODE,
                Permission.EXECUTE_CODE,
                Permission.VIEW_AUTOMATION,
                Permission.CREATE_AUTOMATION,
                Permission.VIEW_ANALYTICS,
                Permission.VIEW_SETTINGS,
                Permission.VIEW_REALTIME,
            },
            Role.VIEWER: {
                Permission.VIEW_DASHBOARD,
                Permission.VIEW_PROJECTS,
                Permission.VIEW_AGENTS,
                Permission.VIEW_CODE,
                Permission.VIEW_AUTOMATION,
                Permission.VIEW_ANALYTICS,
                Permission.VIEW_SETTINGS,
                Permission.VIEW_REALTIME,
            },
            Role.GUEST: {
                Permission.VIEW_DASHBOARD,
            },
        }

        return cls(role=role, permissions=permissions.get(role, set()))


class PermissionManager:
    """Permission management system."""

    def __init__(self):
        self.user_permissions: dict[str, set[Permission]] = {}
        self.role_permissions: dict[Role, set[Permission]] = {}
        self.custom_permissions: dict[str, set[Permission]] = {}

        # Initialize default role permissions
        for role in Role:
            role_perms = RolePermissions.default(role)
            self.role_permissions[role] = role_perms.permissions

    def set_user_permissions(self, user_id: str, permissions: set[Permission]) -> None:
        """Set permissions for a user."""
        self.user_permissions[user_id] = permissions

    def add_user_permission(self, user_id: str, permission: Permission) -> None:
        """Add a permission to a user."""
        if user_id not in self.user_permissions:
            self.user_permissions[user_id] = set()
        self.user_permissions[user_id].add(permission)

    def remove_user_permission(self, user_id: str, permission: Permission) -> None:
        """Remove a permission from a user."""
        if user_id in self.user_permissions:
            self.user_permissions[user_id].discard(permission)

    def get_user_permissions(self, user_id: str) -> set[Permission]:
        """Get all permissions for a user."""
        return self.user_permissions.get(user_id, set())

    def set_user_role(self, user_id: str, role: Role) -> None:
        """Set role for a user."""
        role_perms = self.role_permissions.get(role, set())
        self.user_permissions[user_id] = role_perms.copy()

    def has_permission(self, user_id: str, permission: Permission) -> bool:
        """Check if user has a permission."""
        user_perms = self.user_permissions.get(user_id, set())
        return permission in user_perms

    def has_any_permission(self, user_id: str, permissions: list[Permission]) -> bool:
        """Check if user has any of the permissions."""
        user_perms = self.user_permissions.get(user_id, set())
        return bool(user_perms.intersection(permissions))

    def has_all_permissions(self, user_id: str, permissions: list[Permission]) -> bool:
        """Check if user has all of the permissions."""
        user_perms = self.user_permissions.get(user_id, set())
        return set(permissions).issubset(user_perms)

    def get_role_permissions(self, role: Role) -> set[Permission]:
        """Get permissions for a role."""
        return self.role_permissions.get(role, set())

    def set_role_permissions(self, role: Role, permissions: set[Permission]) -> None:
        """Set permissions for a role."""
        self.role_permissions[role] = permissions

    def add_custom_permission(self, name: str, permissions: set[Permission]) -> None:
        """Add custom permission set."""
        self.custom_permissions[name] = permissions

    def get_custom_permission(self, name: str) -> set[Permission]:
        """Get custom permission set."""
        return self.custom_permissions.get(name, set())

    def apply_custom_permission(self, user_id: str, name: str) -> None:
        """Apply custom permissions to user."""
        custom = self.custom_permissions.get(name, set())
        if user_id not in self.user_permissions:
            self.user_permissions[user_id] = set()
        self.user_permissions[user_id].update(custom)

    def filter_by_permission(self, user_id: str, items: list[Any],
                            key: str = "permission") -> list[Any]:
        """Filter items by user permission."""
        result = []
        for item in items:
            perm_name = item.get(key) if isinstance(item, dict) else getattr(item, key, None)
            if perm_name:
                try:
                    perm = Permission(perm_name)
                    if self.has_permission(user_id, perm):
                        result.append(item)
                except ValueError:
                    pass
        return result

    def get_accessible_routes(self, user_id: str) -> list[str]:
        """Get routes accessible by user."""
        routes = []
        user_perms = self.user_permissions.get(user_id, set())

        # Map permissions to routes
        permission_routes = {
            Permission.VIEW_DASHBOARD: "/dashboard",
            Permission.VIEW_PROJECTS: "/projects",
            Permission.VIEW_AGENTS: "/agents",
            Permission.VIEW_CODE: "/workspace",
            Permission.VIEW_AUTOMATION: "/automation",
            Permission.VIEW_ANALYTICS: "/analytics",
            Permission.VIEW_ADMIN: "/admin",
            Permission.VIEW_BILLING: "/billing",
            Permission.VIEW_SETTINGS: "/settings",
        }

        for perm, route in permission_routes.items():
            if perm in user_perms:
                routes.append(route)

        return routes
