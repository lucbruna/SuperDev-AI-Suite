"""Authorization subsystem."""
from .access_rules import AccessAction, AccessRuleEngine
from .authorization_engine import AuthorizationEngine, Permission
from .permission_manager import PermissionLevel, PermissionManager
from .policy_engine import Effect, PolicyEngine
from .privilege_checker import Privilege, PrivilegeChecker
from .resource_control import ResourceControl, ResourceType
from .role_manager import RoleManager

__all__ = [
    "AuthorizationEngine", "Permission", "PermissionManager", "PermissionLevel",
    "RoleManager", "PolicyEngine", "Effect", "AccessRuleEngine", "AccessAction",
    "PrivilegeChecker", "Privilege", "ResourceControl", "ResourceType",
]
