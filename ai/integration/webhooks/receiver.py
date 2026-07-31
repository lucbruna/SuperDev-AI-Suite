"""
Webhook Receiver - Incoming webhooks
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import json


@dataclass
class ReceivedWebhook:
    received_id: str
    source: str
    event_type: str
    payload: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    signature: str = ""
    verified: bool = False
    processed: bool = False
    received_at: datetime = field(default_factory=datetime.now)


class WebhookReceiver:
    def __init__(self):
        self.received: List[ReceivedWebhook] = []
        self.processors: Dict[str, Any] = {}
        self.secrets: Dict[str, str] = {}

    def receive(self, source: str, event_type: str, payload: Dict[str, Any], headers: Dict[str, str] = None, signature: str = "") -> ReceivedWebhook:
        received_id = hashlib.sha256(f"{source}{event_type}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        webhook = ReceivedWebhook(received_id=received_id, source=source, event_type=event_type, payload=payload, headers=headers or {}, signature=signature)
        self.received.append(webhook)
        return webhook

    def verify_signature(self, received_id: str, secret: str) -> bool:
        webhook = next((w for w in self.received if w.received_id == received_id), None)
        if webhook:
            webhook.verified = True
            return True
        return False

    def process(self, received_id: str) -> bool:
        webhook = next((w for w in self.received if w.received_id == received_id), None)
        if webhook:
            webhook.processed = True
            return True
        return False

    def register_processor(self, event_type: str, processor: Any) -> None:
        self.processors[event_type] = processor

    def set_secret(self, source: str, secret: str) -> None:
        self.secrets[source] = secret

    def get_unprocessed(self) -> List[ReceivedWebhook]:
        return [w for w in self.received if not w.processed]

    def get_recent(self, limit: int = 10) -> List[ReceivedWebhook]:
        return self.received[-limit:]

    def count(self) -> int:
        return len(self.received)
