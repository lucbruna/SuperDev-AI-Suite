"""Cybersecurity Engine Metrics — Metrics tracking for security operations."""

from datetime import datetime
from typing import Any


class SecurityMetrics:
    def __init__(self):
        self._threats_detected: int = 0
        self._vulnerabilities_found: int = 0
        self._incidents_created: int = 0
        self._incidents_resolved: int = 0
        self._login_attempts: int = 0
        self._failed_logins: int = 0
        self._blocked_ips: int = 0
        self._scans_performed: int = 0
        self._events: list[dict[str, Any]] = []

    def record_threat(self) -> None:
        self._threats_detected += 1

    def record_vulnerability(self) -> None:
        self._vulnerabilities_found += 1

    def record_incident(self) -> None:
        self._incidents_created += 1

    def record_resolution(self) -> None:
        self._incidents_resolved += 1

    def record_login(self, success: bool = True) -> None:
        self._login_attempts += 1
        if not success:
            self._failed_logins += 1

    def record_block(self) -> None:
        self._blocked_ips += 1

    def record_scan(self) -> None:
        self._scans_performed += 1

    def add_event(self, event_type: str, details: dict[str, Any] = None) -> None:
        self._events.append(
            {
                "type": event_type,
                "timestamp": datetime.now().isoformat(),
                "details": details or {},
            }
        )

    def get_stats(self) -> dict[str, Any]:
        return {
            "threats_detected": self._threats_detected,
            "vulnerabilities_found": self._vulnerabilities_found,
            "incidents_created": self._incidents_created,
            "incidents_resolved": self._incidents_resolved,
            "login_attempts": self._login_attempts,
            "failed_logins": self._failed_logins,
            "blocked_ips": self._blocked_ips,
            "scans_performed": self._scans_performed,
            "events": len(self._events),
        }

    @property
    def login_success_rate(self) -> float:
        if self._login_attempts == 0:
            return 100.0
        return ((self._login_attempts - self._failed_logins) / self._login_attempts) * 100

    @property
    def incident_resolution_rate(self) -> float:
        if self._incidents_created == 0:
            return 100.0
        return (self._incidents_resolved / self._incidents_created) * 100
