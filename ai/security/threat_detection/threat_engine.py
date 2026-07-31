"""Threat detection engine."""

from __future__ import annotations

import time
import uuid
from enum import Enum
from typing import Any


class ThreatLevel(Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatType(Enum):
    BRUTE_FORCE = "brute_force"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    MALWARE = "malware"
    DATA_EXFILTRATION = "data_exfiltration"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    UNUSUAL_ACCESS = "unusual_access"
    DDOS = "ddos"
    INSIDER_THREAT = "insider_threat"


class Threat:
    def __init__(self, threat_type: ThreatType, level: ThreatLevel, source: str = "", description: str = "") -> None:
        self.threat_id = str(uuid.uuid4())[:8]
        self.type = threat_type
        self.level = level
        self.source = source
        self.description = description
        self.detected_at = time.time()
        self.status = "active"
        self.mitigated = False


class ThreatDetectionEngine:
    def __init__(self) -> None:
        self._threats: dict[str, Threat] = {}
        self._rules: list[dict[str, Any]] = []
        self._blocked_sources: set[str] = set()

    def detect(self, threat_type: ThreatType, level: ThreatLevel, source: str = "", description: str = "") -> Threat:
        threat = Threat(threat_type, level, source, description)
        self._threats[threat.threat_id] = threat
        if level in (ThreatLevel.HIGH, ThreatLevel.CRITICAL):
            self._blocked_sources.add(source)
        return threat

    def add_rule(self, name: str, pattern: str, action: str = "alert", level: ThreatLevel = ThreatLevel.MEDIUM) -> None:
        self._rules.append({"name": name, "pattern": pattern, "action": action, "level": level.value})

    def mitigate(self, threat_id: str, mitigation: str = "") -> bool:
        threat = self._threats.get(threat_id)
        if threat:
            threat.mitigated = True
            threat.status = "mitigated"
            return True
        return False

    def is_source_blocked(self, source: str) -> bool:
        return source in self._blocked_sources

    def unblock_source(self, source: str) -> bool:
        if source in self._blocked_sources:
            self._blocked_sources.remove(source)
            return True
        return False

    def get_threats(self, level: ThreatLevel | None = None, status: str = "") -> list[dict[str, Any]]:
        threats = list(self._threats.values())
        if level:
            threats = [t for t in threats if t.level == level]
        if status:
            threats = [t for t in threats if t.status == status]
        return [
            {
                "id": t.threat_id,
                "type": t.type.value,
                "level": t.level.value,
                "source": t.source,
                "status": t.status,
                "mitigated": t.mitigated,
            }
            for t in threats
        ]

    def stats(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for t in self._threats.values():
            counts[t.level.value] = counts.get(t.level.value, 0) + 1
        return counts
