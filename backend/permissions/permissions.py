from collections import defaultdict


class ProjectPermissions:
    READ = "project:read"
    WRITE = "project:write"
    DELETE = "project:delete"
    ADMIN = "project:admin"


class OrgPermissions:
    READ = "org:read"
    WRITE = "org:write"
    ADMIN = "org:admin"


class UserPermissions:
    READ = "user:read"
    WRITE = "user:write"


class WorkspacePermissions:
    READ = "workspace:read"
    WRITE = "workspace:write"


class AgentPermissions:
    READ = "agent:read"
    WRITE = "agent:write"
    EXECUTE = "agent:execute"


class WorkflowPermissions:
    READ = "workflow:read"
    WRITE = "workflow:write"
    EXECUTE = "workflow:execute"


class PluginPermissions:
    INSTALL = "plugin:install"


class AdminPermissions:
    ACCESS = "admin:access"


ALL_PERMISSIONS = [
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
]

PERMISSION_CATEGORIES: dict[str, list[str]] = defaultdict(list)
_category_map = {
    "project": [ProjectPermissions.READ, ProjectPermissions.WRITE, ProjectPermissions.DELETE, ProjectPermissions.ADMIN],
    "org": [OrgPermissions.READ, OrgPermissions.WRITE, OrgPermissions.ADMIN],
    "user": [UserPermissions.READ, UserPermissions.WRITE],
    "workspace": [WorkspacePermissions.READ, WorkspacePermissions.WRITE],
    "agent": [AgentPermissions.READ, AgentPermissions.WRITE, AgentPermissions.EXECUTE],
    "workflow": [WorkflowPermissions.READ, WorkflowPermissions.WRITE, WorkflowPermissions.EXECUTE],
    "plugin": [PluginPermissions.INSTALL],
    "admin": [AdminPermissions.ACCESS],
}
for category, perms in _category_map.items():
    PERMISSION_CATEGORIES[category] = perms
