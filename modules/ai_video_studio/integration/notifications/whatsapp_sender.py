"""WhatsApp Sender — queues WhatsApp messages to the local outbox."""
from __future__ import annotations

from modules.ai_video_studio.integration.notifications._channel import ChannelSender


class WhatsAppSender(ChannelSender):
    """WhatsApp channel (provider delivery can be wired via config)."""

    channel = "whatsapp"


_whatsapp_sender: WhatsAppSender | None = None


def get_whatsapp_sender() -> WhatsAppSender:
    global _whatsapp_sender
    if _whatsapp_sender is None:
        _whatsapp_sender = WhatsAppSender()
    return _whatsapp_sender
