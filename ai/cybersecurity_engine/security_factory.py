"""Cybersecurity Engine Factory — Factory for creating security components."""

from typing import Any

from .security_models import (
    AuditEntry,
    ComplianceStandard,
    EncryptionKey,
    Incident,
    SecurityPolicy,
    SecurityUser,
    Threat,
    ThreatSeverity,
    ThreatType,
    Vulnerability,
    VulnerabilitySeverity,
)


class SecurityFactory:
    @staticmethod
    def create_threat(
        threat_type: str = "malware",
        severity: str = "low",
        source_ip: str = "",
        target: str = "",
        description: str = "",
    ) -> Threat:
        tt = ThreatType(threat_type) if threat_type in [e.value for e in ThreatType] else ThreatType.MALWARE
        ts = ThreatSeverity(severity) if severity in [e.value for e in ThreatSeverity] else ThreatSeverity.LOW
        return Threat(threat_type=tt, severity=ts, source_ip=source_ip, target=target, description=description)

    @staticmethod
    def create_vulnerability(
        name: str = "", component: str = "", severity: str = "medium", cvss: float = 5.0
    ) -> Vulnerability:
        vs = (
            VulnerabilitySeverity(severity)
            if severity in [e.value for e in VulnerabilitySeverity]
            else VulnerabilitySeverity.MEDIUM
        )
        return Vulnerability(name=name, component=component, severity=vs, cvss_score=cvss)

    @staticmethod
    def create_incident(title: str = "", severity: str = "low", affected_systems: list[str] = None) -> Incident:
        ts = ThreatSeverity(severity) if severity in [e.value for e in ThreatSeverity] else ThreatSeverity.LOW
        return Incident(title=title, severity=ts, affected_systems=affected_systems or [])

    @staticmethod
    def create_user(username: str = "", email: str = "", role: str = "viewer") -> SecurityUser:
        return SecurityUser(username=username, email=email, role=role)

    @staticmethod
    def create_audit_entry(user_id: str = "", action: str = "", resource: str = "", success: bool = True) -> AuditEntry:
        return AuditEntry(user_id=user_id, action=action, resource=resource, success=success)

    @staticmethod
    def create_key(name: str = "", algorithm: str = "AES-256", purpose: str = "") -> EncryptionKey:
        return EncryptionKey(name=name, algorithm=algorithm, purpose=purpose)

    @staticmethod
    def create_policy(name: str = "", standard: str = "lgpd", rules: list[dict[str, Any]] = None) -> SecurityPolicy:
        cs = (
            ComplianceStandard(standard)
            if standard in [e.value for e in ComplianceStandard]
            else ComplianceStandard.LGPD
        )
        return SecurityPolicy(name=name, standard=cs, rules=rules or [])

    @staticmethod
    def templates() -> dict[str, dict[str, Any]]:
        return {
            "web_application": {
                "monitored": ["login", "api", "database"],
                "threat_types": ["xss", "sql_injection", "brute_force"],
                "vuln_severity": "high",
            },
            "infrastructure": {
                "monitored": ["servers", "network", "containers"],
                "threat_types": ["malware", "ddos", "insider"],
                "vuln_severity": "critical",
            },
            "data_platform": {
                "monitored": ["pipelines", "storage", "models"],
                "threat_types": ["data_leak", "unauthorized_access"],
                "vuln_severity": "high",
            },
        }
