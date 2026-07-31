"""Threat detection engine."""
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass, field


class ThreatSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatCategory(Enum):
    MALWARE = "malware"
    PHISHING = "phishing"
    BRUTE_FORCE = "brute_force"
    INSIDER = "insider"
    DDOS = "ddos"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"


@dataclass
class ThreatIndicator:
    indicator_id: str = ""
    indicator_type: str = ""
    value: str = ""
    confidence: float = 0.0
    source: str = ""


@dataclass
class DetectedThreat:
    threat_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    category: ThreatCategory = ThreatCategory.MALWARE
    severity: ThreatSeverity = ThreatSeverity.LOW
    source_ip: str = ""
    target: str = ""
    description: str = ""
    indicators: List[ThreatIndicator] = field(default_factory=list)
    risk_score: float = 0.0
    detected_at: datetime = field(default_factory=datetime.now)
    status: str = "active"


class ThreatDetectionEngine:
    def __init__(self):
        self._threats: Dict[str, DetectedThreat] = {}
        self._rules: List[Dict[str, Any]] = []
        self._blocked_ips: Dict[str, datetime] = {}

    def add_rule(self, name: str, condition: Dict[str, Any], action: str = "alert") -> None:
        self._rules.append({"name": name, "condition": condition, "action": action})

    def analyze_event(self, event: Dict[str, Any]) -> Optional[DetectedThreat]:
        for rule in self._rules:
            cond = rule["condition"]
            match = all(event.get(k) == v for k, v in cond.items() if k != "threshold")
            threshold = cond.get("threshold", 0)
            if match and threshold > 0:
                count = sum(1 for t in self._threats.values() if t.target == event.get("target", ""))
                if count < threshold:
                    continue
            if match:
                threat = DetectedThreat(
                    category=ThreatCategory(event.get("type", "malware")),
                    severity=ThreatSeverity(rule.get("severity", "medium")),
                    source_ip=event.get("source_ip", ""),
                    target=event.get("target", ""),
                    description=f'Rule "{rule["name"]}" triggered',
                    risk_score=0.7,
                )
                self._threats[threat.threat_id] = threat
                return threat
        return None

    def block_ip(self, ip: str) -> bool:
        self._blocked_ips[ip] = datetime.now()
        return True

    def is_blocked(self, ip: str) -> bool:
        return ip in self._blocked_ips

    def get_threats(self, severity: Optional[ThreatSeverity] = None) -> List[DetectedThreat]:
        threats = list(self._threats.values())
        if severity:
            threats = [t for t in threats if t.severity == severity]
        return threats

    def calculate_risk_score(self, threat: DetectedThreat) -> float:
        severity_scores = {ThreatSeverity.LOW: 0.25, ThreatSeverity.MEDIUM: 0.5, ThreatSeverity.HIGH: 0.75, ThreatSeverity.CRITICAL: 1.0}
        return severity_scores.get(threat.severity, 0.5)

    def get_stats(self) -> dict:
        threats = list(self._threats.values())
        return {
            "total_threats": len(threats),
            "critical": len([t for t in threats if t.severity == ThreatSeverity.CRITICAL]),
            "high": len([t for t in threats if t.severity == ThreatSeverity.HIGH]),
            "blocked_ips": len(self._blocked_ips),
            "rules": len(self._rules),
        }
