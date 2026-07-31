"""Cybersecurity Engine — Core cybersecurity engine."""
from datetime import datetime
from typing import Any

from .security_config import CybersecurityConfig
from .security_models import (
    AuditEntry,
    EncryptionKey,
    Incident,
    IncidentStatus,
    SecurityPolicy,
    SecurityUser,
    Threat,
    ThreatSeverity,
    Vulnerability,
    VulnerabilitySeverity,
)


class CybersecurityEngine:
    def __init__(self, config: CybersecurityConfig | None = None):
        self._config = config or CybersecurityConfig()
        self._threats: dict[str, Threat] = {}
        self._vulnerabilities: dict[str, Vulnerability] = {}
        self._incidents: dict[str, Incident] = {}
        self._users: dict[str, SecurityUser] = {}
        self._audit_log: dict[str, AuditEntry] = {}
        self._keys: dict[str, EncryptionKey] = {}
        self._policies: dict[str, SecurityPolicy] = {}

    def report_threat(self, threat: Threat) -> Threat:
        self._threats[threat.threat_id] = threat
        return threat

    def get_threat(self, threat_id: str) -> Threat | None:
        return self._threats.get(threat_id)

    def get_threats(self, severity: ThreatSeverity | None = None) -> list[Threat]:
        threats = list(self._threats.values())
        if severity:
            threats = [t for t in threats if t.severity == severity]
        return threats

    def add_vulnerability(self, vuln: Vulnerability) -> Vulnerability:
        self._vulnerabilities[vuln.vuln_id] = vuln
        return vuln

    def get_vulnerability(self, vuln_id: str) -> Vulnerability | None:
        return self._vulnerabilities.get(vuln_id)

    def get_vulnerabilities(self, severity: VulnerabilitySeverity | None = None) -> list[Vulnerability]:
        vulns = list(self._vulnerabilities.values())
        if severity:
            vulns = [v for v in vulns if v.severity == severity]
        return vulns

    def create_incident(self, incident: Incident) -> Incident:
        self._incidents[incident.incident_id] = incident
        return incident

    def get_incident(self, incident_id: str) -> Incident | None:
        return self._incidents.get(incident_id)

    def update_incident_status(self, incident_id: str, status: IncidentStatus) -> bool:
        incident = self._incidents.get(incident_id)
        if not incident:
            return False
        incident.status = status
        if status in (IncidentStatus.RECOVERED, IncidentStatus.CLOSED):
            incident.resolved_at = datetime.now()
        return True

    def get_incidents(self, status: IncidentStatus | None = None) -> list[Incident]:
        incidents = list(self._incidents.values())
        if status:
            incidents = [i for i in incidents if i.status == status]
        return incidents

    def add_user(self, user: SecurityUser) -> SecurityUser:
        self._users[user.user_id] = user
        return user

    def get_user(self, user_id: str) -> SecurityUser | None:
        return self._users.get(user_id)

    def get_user_by_username(self, username: str) -> SecurityUser | None:
        for u in self._users.values():
            if u.username == username:
                return u
        return None

    def add_audit_entry(self, entry: AuditEntry) -> AuditEntry:
        self._audit_log[entry.entry_id] = entry
        return entry

    def get_audit_log(self, user_id: str | None = None) -> list[AuditEntry]:
        entries = list(self._audit_log.values())
        if user_id:
            entries = [e for e in entries if e.user_id == user_id]
        return entries

    def register_key(self, key: EncryptionKey) -> EncryptionKey:
        self._keys[key.key_id] = key
        return key

    def get_key(self, key_id: str) -> EncryptionKey | None:
        return self._keys.get(key_id)

    def add_policy(self, policy: SecurityPolicy) -> SecurityPolicy:
        self._policies[policy.policy_id] = policy
        return policy

    def get_policy(self, policy_id: str) -> SecurityPolicy | None:
        return self._policies.get(policy_id)

    def get_stats(self) -> dict[str, Any]:
        return {
            "threats": len(self._threats),
            "vulnerabilities": len(self._vulnerabilities),
            "incidents": len(self._incidents),
            "users": len(self._users),
            "audit_entries": len(self._audit_log),
            "encryption_keys": len(self._keys),
            "policies": len(self._policies),
            "active_incidents": len([i for i in self._incidents.values() if i.status not in (IncidentStatus.CLOSED, IncidentStatus.RECOVERED)]),
        }
