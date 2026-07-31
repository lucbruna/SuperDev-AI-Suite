"""
Security Models
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ThreatLevel(Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    CONTAINED = "contained"
    RESOLVED = "resolved"
    CLOSED = "closed"


class AuditAction(Enum):
    LOGIN = "login"
    LOGOUT = "logout"
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    DEPLOY = "deploy"
    ACCESS_DENIED = "access_denied"
    THREAT_DETECTED = "threat_detected"


@dataclass
class User:
    id: str
    username: str
    email: str
    organization_id: str = ""
    roles: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)
    is_active: bool = True
    mfa_enabled: bool = False
    last_login: datetime | None = None
    failed_attempts: int = 0
    locked_until: datetime | None = None

    @property
    def is_locked(self) -> bool:
        if self.locked_until:
            return datetime.now() < self.locked_until
        return False

    def has_role(self, role: str) -> bool:
        return role in self.roles or "admin" in self.roles

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions or "admin" in self.permissions


@dataclass
class Organization:
    id: str
    name: str
    domain: str = ""
    security_level: str = "high"
    policies: list[str] = field(default_factory=list)
    settings: dict[str, Any] = field(default_factory=dict)
    is_active: bool = True


@dataclass
class SecurityEvent:
    id: str
    event_type: str
    source: str
    severity: ThreatLevel = ThreatLevel.LOW
    details: dict[str, Any] = field(default_factory=dict)
    user_id: str | None = None
    ip_address: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)
    resolved: bool = False

    @property
    def is_critical(self) -> bool:
        return self.severity in (ThreatLevel.HIGH, ThreatLevel.CRITICAL)


@dataclass
class Incident:
    id: str
    title: str
    description: str
    severity: ThreatLevel
    status: IncidentStatus = IncidentStatus.OPEN
    assignee: str | None = None
    affected_resources: list[str] = field(default_factory=list)
    timeline: list[dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    resolved_at: datetime | None = None

    def add_timeline_entry(self, entry: str, user: str = "system") -> None:
        self.timeline.append({
            "entry": entry,
            "user": user,
            "timestamp": datetime.now().isoformat()
        })

    def assign(self, assignee: str) -> None:
        self.assignee = assignee
        self.status = IncidentStatus.INVESTIGATING
        self.add_timeline_entry(f"Assigned to {assignee}")

    def resolve(self) -> None:
        self.status = IncidentStatus.RESOLVED
        self.resolved_at = datetime.now()
        self.add_timeline_entry("Incident resolved")


@dataclass
class AuditEntry:
    id: str
    action: AuditAction
    user_id: str
    resource: str = ""
    details: dict[str, Any] = field(default_factory=dict)
    ip_address: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    success: bool = True
    risk_score: float = 0.0
