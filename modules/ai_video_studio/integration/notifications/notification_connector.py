"""Notification Connector — facade over the message senders."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.integration.connector_base import DomainConnector
from modules.ai_video_studio.integration.notifications.email_sender import (
    get_email_sender,
)
from modules.ai_video_studio.integration.notifications.push_sender import (
    get_push_sender,
)
from modules.ai_video_studio.integration.notifications.sms_sender import get_sms_sender
from modules.ai_video_studio.integration.notifications.telegram_sender import (
    get_telegram_sender,
)
from modules.ai_video_studio.integration.notifications.whatsapp_sender import (
    get_whatsapp_sender,
)


class NotificationConnector(DomainConnector):
    """Sends notifications through channel senders (local outbox)."""

    domain = "notifications"
    description = "Email, WhatsApp, Telegram, SMS and push notifications"

    def __init__(self) -> None:
        super().__init__()
        self._register("send_email", lambda d: get_email_sender().send(**d))
        self._register("send_whatsapp", lambda d: get_whatsapp_sender().send(**d))
        self._register("send_telegram", lambda d: get_telegram_sender().send(**d))
        self._register("send_sms", lambda d: get_sms_sender().send(**d))
        self._register("send_push", lambda d: get_push_sender().send(**d))
        self._register("outbox", lambda d: self._outbox())

    def _outbox(self) -> dict[str, Any]:
        return {
            "email": get_email_sender().outbox(),
            "whatsapp": get_whatsapp_sender().outbox(),
            "telegram": get_telegram_sender().outbox(),
            "sms": get_sms_sender().outbox(),
            "push": get_push_sender().outbox(),
        }


_notification_connector: NotificationConnector | None = None


def get_notification_connector() -> NotificationConnector:
    global _notification_connector
    if _notification_connector is None:
        _notification_connector = NotificationConnector()
    return _notification_connector
