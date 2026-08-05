"""Push Sender — queues push notifications to the local outbox."""
from __future__ import annotations

from modules.ai_video_studio.integration.notifications._channel import ChannelSender


class PushSender(ChannelSender):
    """Push channel (FCM/APNs delivery can be wired via config)."""

    channel = "push"


_push_sender: PushSender | None = None


def get_push_sender() -> PushSender:
    global _push_sender
    if _push_sender is None:
        _push_sender = PushSender()
    return _push_sender
