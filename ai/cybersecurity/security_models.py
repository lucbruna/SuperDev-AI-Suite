"""
Security Models
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime


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
    roles: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    is_active: bool = True
    mfa_enabled: bool = False
    last_login: Optional[datetime] = None
    failed_attempts: int = 0
    locked_until: Optional[datetime] = None
    
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
    policies: List[str] = field(default_factory=list)
    settings: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True


@dataclass
class SecurityEvent:
    id: str
    event_type: str
    source: str
    severity: ThreatLevel = ThreatLevel.LOW
    details: Dict[str, Any] = field(default_factory=dict)
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
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
    assignee: Optional[str] = None
    affected_resources: List[str] = field(default_factory=list)
    timeline: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    
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
    details: Dict[str, Any] = field(default_factory=dict)
    ip_address: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    success: bool = True
    risk_score: float = 0.0
