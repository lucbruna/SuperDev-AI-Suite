"""Cybersecurity Engine — Core cybersecurity engine."""
from typing import Dict, Any, Optional, List
from datetime import datetime
from .security_models import (
    Threat, Vulnerability, Incident, SecurityUser, AuditEntry, EncryptionKey, SecurityPolicy,
    ThreatSeverity, ThreatType, IncidentStatus, VulnerabilitySeverity, ComplianceStandard, AccessControl,
)
from .security_config import CybersecurityConfig


class CybersecurityEngine:
    def __init__(self, config: Optional[CybersecurityConfig] = None):
        self._config = config or CybersecurityConfig()
        self._threats: Dict[str, Threat] = {}
        self._vulnerabilities: Dict[str, Vulnerability] = {}
        self._incidents: Dict[str, Incident] = {}
        self._users: Dict[str, SecurityUser] = {}
        self._audit_log: Dict[str, AuditEntry] = {}
        self._keys: Dict[str, EncryptionKey] = {}
        self._policies: Dict[str, SecurityPolicy] = {}

    def report_threat(self, threat: Threat) -> Threat:
        self._threats[threat.threat_id] = threat
        return threat

    def get_threat(self, threat_id: str) -> Optional[Threat]:
        return self._threats.get(threat_id)

    def get_threats(self, severity: Optional[ThreatSeverity] = None) -> List[Threat]:
        threats = list(self._threats.values())
        if severity:
            threats = [t for t in threats if t.severity == severity]
        return threats

    def add_vulnerability(self, vuln: Vulnerability) -> Vulnerability:
        self._vulnerabilities[vuln.vuln_id] = vuln
        return vuln

    def get_vulnerability(self, vuln_id: str) -> Optional[Vulnerability]:
        return self._vulnerabilities.get(vuln_id)

    def get_vulnerabilities(self, severity: Optional[VulnerabilitySeverity] = None) -> List[Vulnerability]:
        vulns = list(self._vulnerabilities.values())
        if severity:
            vulns = [v for v in vulns if v.severity == severity]
        return vulns

    def create_incident(self, incident: Incident) -> Incident:
        self._incidents[incident.incident_id] = incident
        return incident

    def get_incident(self, incident_id: str) -> Optional[Incident]:
        return self._incidents.get(incident_id)

    def update_incident_status(self, incident_id: str, status: IncidentStatus) -> bool:
        incident = self._incidents.get(incident_id)
        if not incident:
            return False
        incident.status = status
        if status in (IncidentStatus.RECOVERED, IncidentStatus.CLOSED):
            incident.resolved_at = datetime.now()
        return True

    def get_incidents(self, status: Optional[IncidentStatus] = None) -> List[Incident]:
        incidents = list(self._incidents.values())
        if status:
            incidents = [i for i in incidents if i.status == status]
        return incidents

    def add_user(self, user: SecurityUser) -> SecurityUser:
        self._users[user.user_id] = user
        return user

    def get_user(self, user_id: str) -> Optional[SecurityUser]:
        return self._users.get(user_id)

    def get_user_by_username(self, username: str) -> Optional[SecurityUser]:
        for u in self._users.values():
            if u.username == username:
                return u
        return None

    def add_audit_entry(self, entry: AuditEntry) -> AuditEntry:
        self._audit_log[entry.entry_id] = entry
        return entry

    def get_audit_log(self, user_id: Optional[str] = None) -> List[AuditEntry]:
        entries = list(self._audit_log.values())
        if user_id:
            entries = [e for e in entries if e.user_id == user_id]
        return entries

    def register_key(self, key: EncryptionKey) -> EncryptionKey:
        self._keys[key.key_id] = key
        return key

    def get_key(self, key_id: str) -> Optional[EncryptionKey]:
        return self._keys.get(key_id)

    def add_policy(self, policy: SecurityPolicy) -> SecurityPolicy:
        self._policies[policy.policy_id] = policy
        return policy

    def get_policy(self, policy_id: str) -> Optional[SecurityPolicy]:
        return self._policies.get(policy_id)

    def get_stats(self) -> Dict[str, Any]:
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
