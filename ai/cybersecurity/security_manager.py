"""
Security Manager
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field


@dataclass
class ManagedResource:
    name: str
    resource_type: str
    owner: str = ""
    security_level: str = "medium"
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class SecurityManager:
    def __init__(self):
        self.resources: Dict[str, ManagedResource] = {}
        self.policies: Dict[str, Any] = {}
        self.audit_log: List[Dict[str, Any]] = []
        
    def register_resource(self, name: str, resource_type: str, **kwargs) -> ManagedResource:
        resource = ManagedResource(name=name, resource_type=resource_type, **kwargs)
        self.resources[name] = resource
        return resource
        
    def unregister_resource(self, name: str) -> bool:
        if name in self.resources:
            del self.resources[name]
            return True
        return False
        
    def get_resource(self, name: str) -> Optional[ManagedResource]:
        return self.resources.get(name)
        
    def list_resources(self) -> List[ManagedResource]:
        return list(self.resources.values())
        
    def list_by_type(self, resource_type: str) -> List[ManagedResource]:
        return [r for r in self.resources.values() if r.resource_type == resource_type]
        
    def add_policy(self, name: str, policy: Any) -> None:
        self.policies[name] = policy
        
    def get_policy(self, name: str) -> Optional[Any]:
        return self.policies.get(name)
        
    def audit(self, action: str, user: str, resource: str, details: Dict[str, Any] = None) -> None:
        self.audit_log.append({
            "action": action,
            "user": user,
            "resource": resource,
            "details": details or {},
        })
        
    def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self.audit_log[-limit:]
