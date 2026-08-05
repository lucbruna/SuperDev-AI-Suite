"""SMS Sender — queues SMS messages to the local outbox."""
from __future__ import annotations

from modules.ai_video_studio.integration.notifications._channel import ChannelSender


class SMSSender(ChannelSender):
    """SMS channel (gateway delivery can be wired via config)."""

    channel = "sms"


_sms_sender: SMSSender | None = None


def get_sms_sender() -> SMSSender:
    global _sms_sender
    if _sms_sender is None:
        _sms_sender = SMSSender()
    return _sms_sender
