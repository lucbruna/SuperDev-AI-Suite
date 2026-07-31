"""
Security Dashboard
"""
from dataclasses import dataclass
from enum import Enum
from typing import Any


class ThreatLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityEvent:
    id: str
    title: str
    threat_level: ThreatLevel
    source: str = ""
    timestamp: str = ""
    description: str = ""
    resolved: bool = False


class SecurityDashboard:
    def __init__(self):
        self.events: list[SecurityEvent] = []
        self.scan_status: str = "idle"
        self.last_scan: str = ""

    def add_event(self, event: SecurityEvent) -> None:
        self.events.insert(0, event)

    def get_active_threats(self) -> list[SecurityEvent]:
        return [e for e in self.events if not e.resolved]

    def get_threat_count_by_level(self) -> dict[str, int]:
        counts = {level.value: 0 for level in ThreatLevel}
        for e in self.get_active_threats():
            counts[e.threat_level.value] += 1
        return counts

    def render(self) -> dict[str, Any]:
        return {
            "events": [{"title": e.title, "threatLevel": e.threat_level.value, "resolved": e.resolved} for e in self.events[:20]],
            "activeThreats": len(self.get_active_threats()),
            "threatCounts": self.get_threat_count_by_level(),
            "scanStatus": self.scan_status,
        }
