"""
Webhook Sender - Outgoing webhooks
"""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class SentWebhook:
    sent_id: str
    url: str
    event_type: str
    payload: dict[str, Any] = field(default_factory=dict)
    headers: dict[str, str] = field(default_factory=dict)
    status: str = "pending"
    response_code: int = 0
    attempts: int = 0
    sent_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime | None = None


class WebhookSender:
    def __init__(self):
        self.sent: list[SentWebhook] = []
        self.default_headers: dict[str, str] = {"Content-Type": "application/json"}
        self.retry_config: dict[str, int] = {"max_retries": 3, "delay_seconds": 5}

    def send(self, url: str, event_type: str, payload: dict[str, Any], headers: dict[str, str] = None) -> SentWebhook:
        sent_id = hashlib.sha256(f"{url}{event_type}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        webhook = SentWebhook(
            sent_id=sent_id,
            url=url,
            event_type=event_type,
            payload=payload,
            headers={**self.default_headers, **(headers or {})},
        )
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

    def retry(self, sent_id: str) -> SentWebhook | None:
        for webhook in self.sent:
            if webhook.sent_id == sent_id and webhook.status == "failed":
                webhook.attempts += 1
                webhook.status = "retrying"
                return webhook
        return None

    def get_sent(self, limit: int = 100) -> list[SentWebhook]:
        return self.sent[-limit:]

    def count(self) -> int:
        return len(self.sent)
