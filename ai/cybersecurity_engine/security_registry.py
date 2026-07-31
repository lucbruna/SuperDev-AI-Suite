"""Cybersecurity Engine Registry — Registry for security components."""
from typing import Dict, Any, List, Optional


class SecurityRegistry:
    def __init__(self):
        self._threats: Dict[str, Dict[str, Any]] = {}
        self._vulnerabilities: Dict[str, Dict[str, Any]] = {}
        self._incidents: Dict[str, Dict[str, Any]] = {}
        self._policies: Dict[str, Dict[str, Any]] = {}

    def register_threat(self, threat_id: str, metadata: Dict[str, Any]) -> None:
        self._threats[threat_id] = metadata

    def get_threat(self, threat_id: str) -> Optional[Dict[str, Any]]:
        return self._threats.get(threat_id)

    def register_vulnerability(self, vuln_id: str, metadata: Dict[str, Any]) -> None:
        self._vulnerabilities[vuln_id] = metadata

    def get_vulnerability(self, vuln_id: str) -> Optional[Dict[str, Any]]:
        return self._vulnerabilities.get(vuln_id)

    def register_incident(self, incident_id: str, metadata: Dict[str, Any]) -> None:
        self._incidents[incident_id] = metadata

    def get_incident(self, incident_id: str) -> Optional[Dict[str, Any]]:
        return self._incidents.get(incident_id)

    def register_policy(self, policy_id: str, metadata: Dict[str, Any]) -> None:
        self._policies[policy_id] = metadata

    def get_policy(self, policy_id: str) -> Optional[Dict[str, Any]]:
        return self._policies.get(policy_id)

    def list_threats(self) -> List[str]:
        return list(self._threats.keys())

    def list_vulnerabilities(self) -> List[str]:
        return list(self._vulnerabilities.keys())

    def list_incidents(self) -> List[str]:
        return list(self._incidents.keys())

    def get_stats(self) -> Dict[str, int]:
        return {
            "threats": len(self._threats),
            "vulnerabilities": len(self._vulnerabilities),
            "incidents": len(self._incidents),
            "policies": len(self._policies),
        }
