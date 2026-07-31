"""Authorization subsystem."""
from .authorization_engine import AuthorizationEngine, Permission
from .permission_manager import PermissionManager, PermissionLevel
from .role_manager import RoleManager
from .policy_engine import PolicyEngine, Effect
from .access_rules import AccessRuleEngine, AccessAction
from .privilege_checker import PrivilegeChecker, Privilege
from .resource_control import ResourceControl, ResourceType

__all__ = [
    "AuthorizationEngine", "Permission", "PermissionManager", "PermissionLevel",
    "RoleManager", "PolicyEngine", "Effect", "AccessRuleEngine", "AccessAction",
    "PrivilegeChecker", "Privilege", "ResourceControl", "ResourceType",
]
