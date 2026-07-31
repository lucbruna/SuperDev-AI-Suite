"""Security data models."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class UserRole(Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    DEVELOPER = "developer"
    VIEWER = "viewer"
    SERVICE = "service"


class Permission(Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    EXECUTE = "execute"
    ADMIN = "admin"


class ThreatLevel(Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AuditAction(Enum):
    LOGIN = "login"
    LOGOUT = "logout"
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    ACCESS_DENIED = "access_denied"
    CONFIG_CHANGE = "config_change"


@dataclass
class UserIdentity:
    user_id: str
    username: str
    email: str
    role: UserRole = UserRole.VIEWER
    organization_id: str = ""
    created_at: float = field(default_factory=time.time)
    last_login: float = 0.0
    is_active: bool = True
    mfa_enabled: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AccessRequest:
    user_id: str
    resource: str
    permission: Permission
    context: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


@dataclass
class AccessDecision:
    allowed: bool
    user_id: str
    resource: str
    permission: Permission
    reason: str = ""
    policy_used: str = ""
    timestamp: float = field(default_factory=time.time)


@dataclass
class AuditEntry:
    entry_id: str
    user_id: str
    action: AuditAction
    resource: str
    details: dict[str, Any] = field(default_factory=dict)
    ip_address: str = ""
    success: bool = True
    timestamp: float = field(default_factory=time.time)


@dataclass
class ThreatEvent:
    event_id: str
    threat_level: ThreatLevel
    source: str
    description: str
    indicators: list[str] = field(default_factory=list)
    blocked: bool = False
    timestamp: float = field(default_factory=time.time)


@dataclass
class SecurityPolicy:
    policy_id: str
    name: str
    rules: list[dict[str, Any]] = field(default_factory=list)
    enabled: bool = True
    priority: int = 0
    created_at: float = field(default_factory=time.time)


@dataclass
class EncryptedData:
    data_id: str
    ciphertext: str
    algorithm: str
    key_id: str
    iv: str = ""
    tag: str = ""
    timestamp: float = field(default_factory=time.time)


@dataclass
class SecretEntry:
    secret_id: str
    name: str
    secret_type: str
    value: str
    created_at: float = field(default_factory=time.time)
    expires_at: float = 0.0
    rotated: bool = False
