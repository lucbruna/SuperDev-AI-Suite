"""Cybersecurity Engine Manager — High-level manager for security operations."""

from typing import Any

from .cybersecurity_engine import CybersecurityEngine
from .security_config import CybersecurityConfig
from .security_models import (
    AccessControl,
    AuditEntry,
    Incident,
    SecurityUser,
    Threat,
    ThreatSeverity,
    ThreatType,
    Vulnerability,
    VulnerabilitySeverity,
)


class SecurityManager:
    def __init__(self, config: CybersecurityConfig | None = None):
        self._engine = CybersecurityEngine(config)

    def report_threat(self, threat_type: str, severity: str, source_ip: str, target: str, description: str) -> Threat:
        tt = ThreatType(threat_type) if threat_type in [e.value for e in ThreatType] else ThreatType.MALWARE
        ts = ThreatSeverity(severity) if severity in [e.value for e in ThreatSeverity] else ThreatSeverity.LOW
        threat = Threat(threat_type=tt, severity=ts, source_ip=source_ip, target=target, description=description)
        return self._engine.report_threat(threat)

    def scan_vulnerability(self, component: str, severity: str = "medium", cvss: float = 5.0) -> Vulnerability:
        vs = (
            VulnerabilitySeverity(severity)
            if severity in [e.value for e in VulnerabilitySeverity]
            else VulnerabilitySeverity.MEDIUM
        )
        vuln = Vulnerability(component=component, severity=vs, cvss_score=cvss, name=f"Vuln in {component}")
        return self._engine.add_vulnerability(vuln)

    def create_incident(self, title: str, severity: str, affected_systems: list[str]) -> Incident:
        ts = ThreatSeverity(severity) if severity in [e.value for e in ThreatSeverity] else ThreatSeverity.LOW
        incident = Incident(title=title, severity=ts, affected_systems=affected_systems)
        return self._engine.create_incident(incident)

    def respond_to_incident(self, incident_id: str, action: str) -> bool:
        incident = self._engine.get_incident(incident_id)
        if not incident:
            return False
        incident.response_actions.append(action)
        return True

    def register_user(self, username: str, email: str, role: str = "viewer") -> SecurityUser:
        user = SecurityUser(username=username, email=email, role=role)
        return self._engine.add_user(user)

    def authenticate(self, username: str, password: str) -> SecurityUser | None:
        user = self._engine.get_user_by_username(username)
        if user and user.is_active:
            user.last_login = __import__("datetime").datetime.now()
            return user
        return None

    def authorize(self, user_id: str, resource: str, action: str) -> bool:
        user = self._engine.get_user(user_id)
        if not user or not user.is_active:
            return False
        if user.role == "admin":
            return True
        if action == "read" and AccessControl.READ in user.permissions:
            return True
        return bool(action == "write" and AccessControl.WRITE in user.permissions)

    def log_audit(self, user_id: str, action: str, resource: str, success: bool = True) -> AuditEntry:
        entry = AuditEntry(user_id=user_id, action=action, resource=resource, success=success)
        return self._engine.add_audit_entry(entry)

    def get_threats(self, severity: str | None = None) -> list[Threat]:
        if severity:
            sev = ThreatSeverity(severity)
            return self._engine.get_threats(sev)
        return self._engine.get_threats()

    def get_stats(self) -> dict[str, Any]:
        return self._engine.get_stats()
