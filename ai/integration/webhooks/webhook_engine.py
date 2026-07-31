"""
Webhook Engine - Core webhook management
"""
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import hashlib
import json


class WebhookStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAILED = "failed"


@dataclass
class Webhook:
    webhook_id: str
    name: str
    url: str
    events: List[str] = field(default_factory=list)
    secret: str = ""
    status: WebhookStatus = WebhookStatus.ACTIVE
    headers: Dict[str, str] = field(default_factory=dict)
    retry_count: int = 3
    created_at: datetime = field(default_factory=datetime.now)
    last_triggered: Optional[datetime] = None
    failure_count: int = 0


@dataclass
class WebhookEvent:
    event_id: str
    webhook_id: str
    event_type: str
    payload: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"
    attempts: int = 0
    response_code: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


class WebhookEngine:
    def __init__(self):
        self.webhooks: Dict[str, Webhook] = {}
        self.events: List[WebhookEvent] = []
        self.handlers: Dict[str, List[Callable]] = {}

    def register_webhook(self, name: str, url: str, events: List[str] = None, **kwargs) -> Webhook:
        webhook_id = hashlib.sha256(f"{name}{url}".encode()).hexdigest()[:16]
        webhook = Webhook(webhook_id=webhook_id, name=name, url=url, events=events or ["*"], **kwargs)
        self.webhooks[webhook_id] = webhook
        return webhook

    def unregister_webhook(self, webhook_id: str) -> bool:
        if webhook_id in self.webhooks:
            del self.webhooks[webhook_id]
            return True
        return False

    def trigger_event(self, event_type: str, payload: Dict[str, Any]) -> List[WebhookEvent]:
        triggered = []
        for webhook in self.webhooks.values():
            if webhook.status == WebhookStatus.ACTIVE and (event_type in webhook.events or "*" in webhook.events):
                event = WebhookEvent(event_id=hashlib.sha256(f"{webhook.webhook_id}{event_type}{datetime.now().isoformat()}".encode()).hexdigest()[:16], webhook_id=webhook.webhook_id, event_type=event_type, payload=payload)
                self.events.append(event)
                webhook.last_triggered = datetime.now()
                triggered.append(event)
        return triggered

    def handle_response(self, event_id: str, status: str, response_code: int = 200) -> bool:
        for event in self.events:
            if event.event_id == event_id:
                event.status = status
                event.response_code = response_code
                event.completed_at = datetime.now()
                return True
        return False

    def get_webhook(self, webhook_id: str) -> Optional[Webhook]:
        return self.webhooks.get(webhook_id)

    def list_webhooks(self) -> List[Webhook]:
        return list(self.webhooks.values())

    def get_events(self, webhook_id: str = None) -> List[WebhookEvent]:
        if webhook_id:
            return [e for e in self.events if e.webhook_id == webhook_id]
        return self.events

    def count(self) -> int:
        return len(self.webhooks)
