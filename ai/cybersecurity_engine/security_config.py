"""Cybersecurity Engine Config — Configuration for the cybersecurity platform."""
from dataclasses import dataclass, field
from typing import Dict, Any, List


@dataclass
class CybersecurityConfig:
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 30
    session_timeout_minutes: int = 60
    password_min_length: int = 12
    require_mfa: bool = True
    threat_scan_interval_seconds: int = 300
    vulnerability_scan_interval_hours: int = 24
    audit_log_retention_days: int = 365
    encryption_algorithm: str = "AES-256-GCM"
    max_concurrent_sessions: int = 3
    alert_severity_threshold: str = "medium"
    auto_block_threshold: float = 0.8
    compliance_standards: List[str] = field(default_factory=lambda: ["LGPD", "SOC2"])
    monitored_resources: List[str] = field(default_factory=lambda: ["servers", "databases", "apis", "users"])
