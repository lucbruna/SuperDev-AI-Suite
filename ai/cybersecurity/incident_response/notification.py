"""
Incident Notification System
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class NotificationChannel(Enum):
    EMAIL = "email"
    SMS = "sms"
    SLACK = "slack"
    WEBHOOK = "webhook"
    PAGERDUTY = "pagerduty"


class Priority(Enum):
    URGENT = "urgent"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


@dataclass
class NotificationTemplate:
    template_id: str
    name: str
    subject: str = ""
    body: str = ""
    channels: list[NotificationChannel] = field(default_factory=list)


@dataclass
class Notification:
    notification_id: str
    template_id: str
    recipient: str
    channel: NotificationChannel
    priority: Priority = Priority.NORMAL
    sent: bool = False
    sent_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EscalationRule:
    rule_id: str
    name: str
    severity_threshold: str = "high"
    delay_minutes: int = 30
    recipients: list[str] = field(default_factory=list)
    channels: list[NotificationChannel] = field(default_factory=list)


class NotificationSystem:
    def __init__(self):
        self.templates: dict[str, NotificationTemplate] = {}
        self.notifications: list[Notification] = []
        self.escalation_rules: dict[str, EscalationRule] = {}

    def create_template(self, name: str, subject: str = "", body: str = "", channels: list[NotificationChannel] = None) -> NotificationTemplate:
        template_id = f"tpl_{len(self.templates)}"
        template = NotificationTemplate(template_id=template_id, name=name, subject=subject, body=body, channels=channels or [NotificationChannel.EMAIL])
        self.templates[template_id] = template
        return template

    def send_notification(self, template_id: str, recipient: str, channel: NotificationChannel = NotificationChannel.EMAIL, priority: Priority = Priority.NORMAL) -> Notification:
        notification = Notification(notification_id=f"notif_{len(self.notifications)}", template_id=template_id, recipient=recipient, channel=channel, priority=priority, sent=True, sent_at=datetime.now())
        self.notifications.append(notification)
        return notification

    def add_escalation_rule(self, name: str, severity_threshold: str = "high", delay_minutes: int = 30, recipients: list[str] = None) -> EscalationRule:
        rule_id = f"esc_{len(self.escalation_rules)}"
        rule = EscalationRule(rule_id=rule_id, name=name, severity_threshold=severity_threshold, delay_minutes=delay_minutes, recipients=recipients or [])
        self.escalation_rules[rule_id] = rule
        return rule

    def get_notifications(self, recipient: str = None, sent: bool = None) -> list[Notification]:
        results = self.notifications
        if recipient:
            results = [n for n in results if n.recipient == recipient]
        if sent is not None:
            results = [n for n in results if n.sent == sent]
        return results

    def get_template(self, template_id: str) -> NotificationTemplate | None:
        return self.templates.get(template_id)

    def get_escalation_rules(self) -> list[EscalationRule]:
        return list(self.escalation_rules.values())

    def count(self) -> int:
        return len(self.notifications)
