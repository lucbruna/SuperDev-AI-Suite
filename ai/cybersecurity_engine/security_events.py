"""Cybersecurity Engine Events — Event definitions for security operations."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class SecurityEventType(Enum):
    THREAT_DETECTED = "threat_detected"
    VULNERABILITY_FOUND = "vulnerability_found"
    INCIDENT_CREATED = "incident_created"
    INCIDENT_RESOLVED = "incident_resolved"
    USER_LOGIN = "user_login"
    USER_LOGIN_FAILED = "user_login_failed"
    ACCESS_GRANTED = "access_granted"
    ACCESS_DENIED = "access_denied"
    DATA_EXPORT = "data_export"
    CONFIG_CHANGED = "config_changed"


@dataclass
class SecurityEvent:
    event_id: str = ""
    event_type: SecurityEventType = SecurityEventType.THREAT_DETECTED
    source: str = ""
    target: str = ""
    details: dict[str, Any] = field(default_factory=dict)
    severity: str = "info"
    timestamp: datetime = field(default_factory=datetime.now)
