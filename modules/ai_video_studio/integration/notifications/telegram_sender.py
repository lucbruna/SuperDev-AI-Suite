"""Telegram Sender — queues Telegram messages to the local outbox."""
from __future__ import annotations

from modules.ai_video_studio.integration.notifications._channel import ChannelSender


class TelegramSender(ChannelSender):
    """Telegram channel (bot delivery can be wired via config)."""

    channel = "telegram"


_telegram_sender: TelegramSender | None = None


def get_telegram_sender() -> TelegramSender:
    global _telegram_sender
    if _telegram_sender is None:
        _telegram_sender = TelegramSender()
    return _telegram_sender
