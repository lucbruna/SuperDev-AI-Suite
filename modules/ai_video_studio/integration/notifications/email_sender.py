"""Email Sender — queues email notifications to the local outbox."""
from __future__ import annotations

from modules.ai_video_studio.integration.notifications._channel import ChannelSender


class EmailSender(ChannelSender):
    """Email channel (SMTP delivery can be wired via config)."""

    channel = "email"


_email_sender: EmailSender | None = None


def get_email_sender() -> EmailSender:
    global _email_sender
    if _email_sender is None:
        _email_sender = EmailSender()
    return _email_sender
