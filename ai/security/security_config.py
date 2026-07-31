"""Security & Compliance Engine — Volume 17 core configuration."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class SecurityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ComplianceStandard(Enum):
    LGPD = "lgpd"
    GDPR = "gdpr"
    SOC2 = "soc2"
    ISO27001 = "iso27001"
    PCIDSS = "pci_dss"
    HIPAA = "hipaa"


class AuthMethod(Enum):
    PASSWORD = "password"
    MFA = "mfa"
    OAUTH = "oauth"
    BIOMETRIC = "biometric"
    API_KEY = "api_key"
    TOKEN = "token"


@dataclass
class EncryptionConfig:
    algorithm: str = "AES-256-GCM"
    key_size: int = 256
    rotation_days: int = 90
    at_rest: bool = True
    in_transit: bool = True


@dataclass
class PasswordPolicy:
    min_length: int = 12
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_digits: bool = True
    require_special: bool = True
    max_age_days: int = 90
    history_count: int = 5


@dataclass
class SessionConfig:
    timeout_minutes: int = 30
    max_concurrent: int = 3
    extend_on_activity: bool = True
    secure_cookies: bool = True


@dataclass
class AuditConfig:
    enabled: bool = True
    log_level: str = "INFO"
    retention_days: int = 365
    real_time_alerts: bool = True


@dataclass
class FirewallConfig:
    enabled: bool = True
    default_action: str = "deny"
    rate_limit_rpm: int = 1000
    blocked_ips: list[str] = field(default_factory=list)


@dataclass
class ThreatDetectionConfig:
    enabled: bool = True
    anomaly_threshold: float = 0.7
    auto_block: bool = False
    alert_channels: list[str] = field(default_factory=lambda: ["log"])


@dataclass
class SecurityConfig:
    level: SecurityLevel = SecurityLevel.HIGH
    encryption: EncryptionConfig = field(default_factory=EncryptionConfig)
    password_policy: PasswordPolicy = field(default_factory=PasswordPolicy)
    session: SessionConfig = field(default_factory=SessionConfig)
    audit: AuditConfig = field(default_factory=AuditConfig)
    firewall: FirewallConfig = field(default_factory=FirewallConfig)
    threat_detection: ThreatDetectionConfig = field(default_factory=ThreatDetectionConfig)
    compliance_standards: list[ComplianceStandard] = field(
        default_factory=lambda: [ComplianceStandard.LGPD, ComplianceStandard.SOC2]
    )
    agent_security_enabled: bool = True
    api_protection_enabled: bool = True
