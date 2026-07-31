"""
Security Information and Event Management
"""
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class EventType(Enum):
    AUTH_SUCCESS = "auth_success"
    AUTH_FAILURE = "auth_failure"
    NETWORK_ANOMALY = "network_anomaly"
    FILE_ACCESS = "file_access"
    SYSTEM_CHANGE = "system_change"
    MALWARE = "malware"
    PRIVILEGE_ESCALATION = "privilege_escalation"


class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class LogEvent:
    event_id: str
    event_type: EventType
    source: str
    message: str
    severity: Severity = Severity.INFO
    timestamp: datetime = field(default_factory=datetime.now)
    raw_data: dict[str, Any] = field(default_factory=dict)
    normalized: bool = False


@dataclass
class CorrelationRule:
    rule_id: str
    name: str
    conditions: dict[str, Any] = field(default_factory=dict)
    severity: Severity = Severity.MEDIUM
    enabled: bool = True
    description: str = ""


@dataclass
class SIEMAlert:
    alert_id: str
    rule_id: str
    events: list[str] = field(default_factory=list)
    severity: Severity = Severity.MEDIUM
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False


# Fix the enum name issue
class _EventType(Enum):
    AUTH_SUCCESS = "auth_success"
    AUTH_FAILURE = "auth_failure"
    NETWORK_ANOMALY = "network_anomaly"
    FILE_ACCESS = "file_access"
    SYSTEM_CHANGE = "system_change"
    MALWARE = "malware"
    PRIVILEGE_ESCALATION = "privilege_escalation"


class SIEMEngine:
    def __init__(self):
        self.events: list[LogEvent] = []
        self.rules: dict[str, CorrelationRule] = {}
        self.alerts: list[SIEMAlert] = []

    def ingest_event(self, event_type: EventType, source: str, message: str, raw_data: dict[str, Any] = None) -> LogEvent:
        event_id = hashlib.sha256(f"{source}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        event = LogEvent(event_id=event_id, event_type=event_type, source=source, message=message, raw_data=raw_data or {}, normalized=True)
        self.events.append(event)
        self._check_rules(event)
        return event

    def _check_rules(self, event: LogEvent) -> None:
        for rule in self.rules.values():
            if not rule.enabled:
                continue
            matching_events = [e for e in self.events if e.event_type.value in rule.conditions.get("event_types", [])]
            if len(matching_events) >= rule.conditions.get("count", 1):
                alert = SIEMAlert(alert_id=hashlib.sha256(rule.rule_id.encode()).hexdigest()[:16], rule_id=rule.rule_id, events=[e.event_id for e in matching_events], severity=rule.severity, message=f"Rule triggered: {rule.name}")
                self.alerts.append(alert)

    def add_rule(self, name: str, conditions: dict[str, Any], severity: Severity = Severity.MEDIUM) -> CorrelationRule:
        rule_id = hashlib.sha256(name.encode()).hexdigest()[:16]
        rule = CorrelationRule(rule_id=rule_id, name=name, conditions=conditions, severity=severity)
        self.rules[rule_id] = rule
        return rule

    def search_events(self, query: str) -> list[LogEvent]:
        return [e for e in self.events if query.lower() in e.message.lower() or query.lower() in e.source.lower()]

    def get_events_by_type(self, event_type: EventType) -> list[LogEvent]:
        return [e for e in self.events if e.event_type == event_type]

    def get_alerts(self, acknowledged: bool = False) -> list[SIEMAlert]:
        return [a for a in self.alerts if a.acknowledged == acknowledged]

    def acknowledge_alert(self, alert_id: str) -> bool:
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                return True
        return False

    def count(self) -> int:
        return len(self.events)
