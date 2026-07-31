"""Knowledge Security — Security controls for the knowledge platform."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class AccessPermission(Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"


@dataclass
class AccessPolicy:
    policy_id: str = ""
    user_role: str = ""
    resource_type: str = ""
    permissions: list[AccessPermission] = field(default_factory=list)
    conditions: dict[str, Any] = field(default_factory=dict)


class KnowledgeSecurity:
    def __init__(self):
        self._policies: dict[str, AccessPolicy] = {}
        self._access_log: list[dict[str, Any]] = []
        self._encryption_keys: dict[str, str] = {}

    def add_policy(self, policy: AccessPolicy) -> None:
        self._policies[policy.policy_id] = policy

    def check_access(self, user_role: str, resource_type: str, permission: AccessPermission) -> bool:
        for policy in self._policies.values():
            if policy.user_role == user_role and policy.resource_type == resource_type:
                if permission in policy.permissions:
                    return True
        return False

    def log_access(self, user_id: str, resource: str, permission: str, granted: bool) -> None:
        self._access_log.append({
            "user_id": user_id,
            "resource": resource,
            "permission": permission,
            "granted": granted,
            "timestamp": datetime.now().isoformat(),
        })

    def encrypt_content(self, content: str, key_id: str = "default") -> str:
        return f"encrypted:{len(content)}"

    def decrypt_content(self, encrypted: str, key_id: str = "default") -> str:
        if encrypted.startswith("encrypted:"):
            return "decrypted_content"
        return encrypted

    def get_access_log(self, user_id: str | None = None) -> list[dict[str, Any]]:
        log = list(self._access_log)
        if user_id:
            log = [e for e in log if e["user_id"] == user_id]
        return log

    def get_stats(self) -> dict[str, Any]:
        return {
            "total_policies": len(self._policies),
            "total_access_logs": len(self._access_log),
            "denied_access": len([e for e in self._access_log if not e["granted"]]),
        }
