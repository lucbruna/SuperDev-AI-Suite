"""Cybersecurity Engine Models — Core data models for the cybersecurity platform."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ThreatSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatType(Enum):
    MALWARE = "malware"
    PHISHING = "phishing"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    BRUTE_FORCE = "brute_force"
    DDOS = "ddos"
    INSIDER = "insider"
    ZERO_DAY = "zero_day"
    RANSOMWARE = "ransomware"
    MAN_IN_THE_MIDDLE = "man_in_the_middle"


class IncidentStatus(Enum):
    DETECTED = "detected"
    INVESTIGATING = "investigating"
    CONTAINED = "contained"
    ERADICATED = "eradicated"
    RECOVERED = "recovered"
    CLOSED = "closed"


class VulnerabilitySeverity(Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ComplianceStandard(Enum):
    LGPD = "lgpd"
    GDPR = "gdpr"
    HIPAA = "hipaa"
    SOC2 = "soc2"
    PCI_DSS = "pci_dss"
    ISO27001 = "iso27001"


class AccessControl(Enum):
    NONE = "none"
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    ADMIN = "admin"


@dataclass
class Threat:
    threat_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    threat_type: ThreatType = ThreatType.MALWARE
    severity: ThreatSeverity = ThreatSeverity.LOW
    source_ip: str = ""
    target: str = ""
    description: str = ""
    indicators: list[str] = field(default_factory=list)
    detected_at: datetime = field(default_factory=datetime.now)
    status: str = "active"


@dataclass
class Vulnerability:
    vuln_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    severity: VulnerabilitySeverity = VulnerabilitySeverity.LOW
    component: str = ""
    description: str = ""
    cvss_score: float = 0.0
    remediation: str = ""
    discovered_at: datetime = field(default_factory=datetime.now)
    status: str = "open"


@dataclass
class Incident:
    incident_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    severity: ThreatSeverity = ThreatSeverity.LOW
    status: IncidentStatus = IncidentStatus.DETECTED
    threats: list[str] = field(default_factory=list)
    affected_systems: list[str] = field(default_factory=list)
    response_actions: list[str] = field(default_factory=list)
    assigned_to: str = ""
    detected_at: datetime = field(default_factory=datetime.now)
    resolved_at: datetime | None = None


@dataclass
class SecurityUser:
    user_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    username: str = ""
    email: str = ""
    role: str = "viewer"
    permissions: list[AccessControl] = field(default_factory=list)
    is_active: bool = True
    last_login: datetime | None = None
    failed_attempts: int = 0
    locked_until: datetime | None = None


@dataclass
class AuditEntry:
    entry_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    user_id: str = ""
    action: str = ""
    resource: str = ""
    details: dict[str, Any] = field(default_factory=dict)
    success: bool = True
    ip_address: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class EncryptionKey:
    key_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    algorithm: str = "AES-256"
    purpose: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime | None = None
    is_active: bool = True


@dataclass
class SecurityPolicy:
    policy_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    rules: list[dict[str, Any]] = field(default_factory=list)
    standard: ComplianceStandard = ComplianceStandard.LGPD
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
