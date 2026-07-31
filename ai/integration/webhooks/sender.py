"""
Webhook Sender - Outgoing webhooks
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import json


@dataclass
class SentWebhook:
    sent_id: str
    url: str
    event_type: str
    payload: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    status: str = "pending"
    response_code: int = 0
    attempts: int = 0
    sent_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


class WebhookSender:
    def __init__(self):
        self.sent: List[SentWebhook] = []
        self.default_headers: Dict[str, str] = {"Content-Type": "application/json"}
        self.retry_config: Dict[str, int] = {"max_retries": 3, "delay_seconds": 5}

    def send(self, url: str, event_type: str, payload: Dict[str, Any], headers: Dict[str, str] = None) -> SentWebhook:
        sent_id = hashlib.sha256(f"{url}{event_type}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        webhook = SentWebhook(sent_id=sent_id, url=url, event_type=event_type, payload=payload, headers={**self.default_headers, **(headers or {})})
        self.sent.append(webhook)
        return webhook

    def mark_sent(self, sent_id: str, response_code: int = 200) -> bool:
        for webhook in self.sent:
            if webhook.sent_id == sent_id:
                webhook.status = "sent"
                webhook.response_code = response_code
                webhook.completed_at = datetime.now()
                return True
        return False

    def retry(self, sent_id: str) -> Optional[SentWebhook]:
        for webhook in self.sent:
            if webhook.sent_id == sent_id and webhook.status == "failed":
                webhook.attempts += 1
                webhook.status = "retrying"
                return webhook
        return None

    def get_sent(self, limit: int = 100) -> List[SentWebhook]:
        return self.sent[-limit:]

    def count(self) -> int:
        return len(self.sent)
