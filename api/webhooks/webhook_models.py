from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class WebhookStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"
    FAILED = "failed"


class WebhookEvent(str, Enum):
    ALL = "*"
    ROUTE_CREATED = "route.created"
    ROUTE_UPDATED = "route.updated"
    ROUTE_DELETED = "route.deleted"
    AUTH_LOGIN = "auth.login"
    AUTH_LOGOUT = "auth.logout"
    AUTH_FAILED = "auth.failed"
    API_CALL = "api.call"
    API_ERROR = "api.error"
    EVENT_PUBLISHED = "event.published"
    WEBHOOK_DELIVERED = "webhook.delivered"
    WEBHOOK_FAILED = "webhook.failed"


@dataclass
class Webhook:
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    url: str = ""
    events: list[str] = field(default_factory=lambda: [WebhookEvent.ALL])
    secret: str = ""
    status: WebhookStatus = WebhookStatus.ACTIVE
    retry_count: int = 3
    timeout: float = 10.0
    headers: dict[str, str] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    last_delivery: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
