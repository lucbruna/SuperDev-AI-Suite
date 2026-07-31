"""Mobile Security - Device and data security for mobile/edge."""
import hashlib
import secrets
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class SecurityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatType(Enum):
    NONE = "none"
    MALWARE = "malware"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_BREACH = "data_breach"
    MAN_IN_MIDDLE = "man_in_middle"
    DEVICE_THEFT = "device_theft"


@dataclass
class SecurityPolicy:
    policy_id: str
    name: str
    level: SecurityLevel = SecurityLevel.MEDIUM
    require_biometric: bool = False
    require_encryption: bool = True
    max_failed_attempts: int = 5
    lockout_minutes: int = 30
    allowed_platforms: list[str] = field(default_factory=list)
    settings: dict[str, Any] = field(default_factory=dict)


@dataclass
class DeviceSecurity:
    device_id: str
    is_encrypted: bool = False
    is_rooted: bool = False
    threat_level: ThreatType = ThreatType.NONE
    last_scan: datetime | None = None
    failed_attempts: int = 0
    locked_until: datetime | None = None
    certificates: list[str] = field(default_factory=list)


class MobileSecurityManager:
    def __init__(self):
        self.policies: dict[str, SecurityPolicy] = {}
        self.device_security: dict[str, DeviceSecurity] = {}
        self.audit_log: list[dict[str, Any]] = []
        self.tokens: dict[str, dict[str, Any]] = {}

    def create_policy(self, name: str, level: SecurityLevel = SecurityLevel.MEDIUM, **kwargs) -> SecurityPolicy:
        policy_id = hashlib.sha256(f"{name}{level.value}".encode()).hexdigest()[:16]
        policy = SecurityPolicy(policy_id=policy_id, name=name, level=level, **kwargs)
        self.policies[policy_id] = policy
        return policy

    def get_policy(self, policy_id: str) -> SecurityPolicy | None:
        return self.policies.get(policy_id)

    def register_device_security(self, device_id: str) -> DeviceSecurity:
        sec = DeviceSecurity(device_id=device_id)
        self.device_security[device_id] = sec
        return sec

    def scan_device(self, device_id: str) -> ThreatType:
        sec = self.device_security.get(device_id)
        if sec:
            sec.last_scan = datetime.now()
            self._audit("scan", device_id)
            return sec.threat_level
        return ThreatType.NONE

    def lock_device(self, device_id: str, minutes: int = 30) -> bool:
        sec = self.device_security.get(device_id)
        if sec:
            sec.locked_until = datetime.now().timestamp() + minutes * 60
            self._audit("lock", device_id, {"minutes": minutes})
            return True
        return False

    def is_device_locked(self, device_id: str) -> bool:
        sec = self.device_security.get(device_id)
        if sec and sec.locked_until:
            return datetime.now().timestamp() < sec.locked_until
        return False

    def record_failed_attempt(self, device_id: str) -> int:
        sec = self.device_security.get(device_id)
        if sec:
            sec.failed_attempts += 1
            self._audit("failed_attempt", device_id, {"attempts": sec.failed_attempts})
            return sec.failed_attempts
        return 0

    def generate_token(self, device_id: str, scope: str = "api") -> str:
        token = secrets.token_urlsafe(32)
        self.tokens[token] = {"device_id": device_id, "scope": scope, "created_at": datetime.now().isoformat()}
        return token

    def validate_token(self, token: str) -> bool:
        return token in self.tokens

    def revoke_token(self, token: str) -> bool:
        if token in self.tokens:
            del self.tokens[token]
            return True
        return False

    def get_audit_log(self, limit: int = 100) -> list[dict[str, Any]]:
        return self.audit_log[-limit:]

    def _audit(self, action: str, device_id: str, data: dict[str, Any] = None):
        self.audit_log.append({"action": action, "device_id": device_id, "data": data or {}, "timestamp": datetime.now().isoformat()})

    def count_policies(self) -> int:
        return len(self.policies)
