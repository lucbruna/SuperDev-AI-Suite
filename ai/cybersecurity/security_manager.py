"""
Security Manager
"""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ManagedResource:
    name: str
    resource_type: str
    owner: str = ""
    security_level: str = "medium"
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class SecurityManager:
    def __init__(self):
        self.resources: dict[str, ManagedResource] = {}
        self.policies: dict[str, Any] = {}
        self.audit_log: list[dict[str, Any]] = []

    def register_resource(self, name: str, resource_type: str, **kwargs) -> ManagedResource:
        resource = ManagedResource(name=name, resource_type=resource_type, **kwargs)
        self.resources[name] = resource
        return resource

    def unregister_resource(self, name: str) -> bool:
        if name in self.resources:
            del self.resources[name]
            return True
        return False

    def get_resource(self, name: str) -> ManagedResource | None:
        return self.resources.get(name)

    def list_resources(self) -> list[ManagedResource]:
        return list(self.resources.values())

    def list_by_type(self, resource_type: str) -> list[ManagedResource]:
        return [r for r in self.resources.values() if r.resource_type == resource_type]

    def add_policy(self, name: str, policy: Any) -> None:
        self.policies[name] = policy

    def get_policy(self, name: str) -> Any | None:
        return self.policies.get(name)

    def audit(self, action: str, user: str, resource: str, details: dict[str, Any] = None) -> None:
        self.audit_log.append({
            "action": action,
            "user": user,
            "resource": resource,
            "details": details or {},
        })

    def get_audit_log(self, limit: int = 100) -> list[dict[str, Any]]:
        return self.audit_log[-limit:]
