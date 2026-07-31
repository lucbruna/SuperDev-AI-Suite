"""Threat detection subsystem (Volume 16) — heuristics over security events."""

from __future__ import annotations

import time
from typing import Any

from ..security_models import ThreatEvent, ThreatSeverity, ThreatStatus


class ThreatDetectionEngine:
    """Detect threats from event streams using simple heuristics."""

    name = "threat_detection"
    description = "Threat and anomaly detection over security events"

    def __init__(self, engine: Any | None = None) -> None:
        self.engine = engine
        self._events: list[dict[str, Any]] = []
        self._threats: dict[str, ThreatEvent] = {}
        self._failed_logins: dict[str, list[float]] = {}
        self._max_failed_logins = 5
        self._window_seconds = 300.0

    # -- heuristics ----------------------------------------------------------

    def _register_threat(
        self,
        title: str,
        source: str,
        severity: ThreatSeverity,
        details: dict[str, Any],
    ) -> ThreatEvent:
        threat = ThreatEvent(
            title=title,
            source=source,
            severity=severity,
            details=details,
        )
        self._threats[threat.threat_id] = threat
        if self.engine is not None:
            self.engine.registry.register_threat(threat)
            self.engine.metrics.increment(
                "security.threats", labels={"severity": severity.value}
            )
        return threat

    def ingest(self, event_type: str, source: str, data: dict[str, Any] | None = None) -> list[ThreatEvent]:
        """Process a raw event and return any threats it triggers."""
        data = data or {}
        event = {"type": event_type, "source": source, "data": data, "ts": time.time()}
        self._events.append(event)
        threats: list[ThreatEvent] = []

        if event_type == "login.failed":
            key = data.get("username", source)
            self._failed_logins.setdefault(key, []).append(time.time())
            self._failed_logins[key] = [
                t for t in self._failed_logins[key] if t >= time.time() - self._window_seconds
            ]
            if len(self._failed_logins[key]) >= self._max_failed_logins:
                threats.append(
                    self._register_threat(
                        "Brute-force login attempt",
                        source,
                        ThreatSeverity.HIGH,
                        {"username": key, "failures": len(self._failed_logins[key])},
                    )
                )

        if event_type == "api.key.used" and data.get("over_quota"):
            threats.append(
                self._register_threat(
                    "API key quota exceeded", source, ThreatSeverity.MEDIUM, data
                )
            )

        if event_type == "vault.access" and data.get("unauthorized"):
            threats.append(
                self._register_threat(
                    "Unauthorized vault access", source, ThreatSeverity.CRITICAL, data
                )
            )

        if event_type == "data.export" and data.get("volume_mb", 0) > 100:
            threats.append(
                self._register_threat(
                    "Suspicious data exfiltration", source, ThreatSeverity.HIGH, data
                )
            )
        return threats

    # -- lifecycle -----------------------------------------------------------

    def mitigate(self, threat_id: str) -> bool:
        threat = self._threats.get(threat_id)
        if threat is None:
            return False
        threat.status = ThreatStatus.MITIGATED
        threat.mitigated = True
        if self.engine is not None:
            self.engine.metrics.increment("security.threats_mitigated")
        return True

    def accept(self, threat_id: str) -> bool:
        threat = self._threats.get(threat_id)
        if threat is None:
            return False
        threat.status = ThreatStatus.ACCEPTED
        return True

    def list_threats(self, status: ThreatStatus | None = None) -> list[ThreatEvent]:
        if status is None:
            return list(self._threats.values())
        return [t for t in self._threats.values() if t.status == status]

    def events(self, limit: int = 100) -> list[dict[str, Any]]:
        return self._events[-limit:]

    def status(self) -> dict[str, Any]:
        return {
            "events": len(self._events),
            "threats": len(self._threats),
            "open": sum(1 for t in self._threats.values() if not t.mitigated),
        }
