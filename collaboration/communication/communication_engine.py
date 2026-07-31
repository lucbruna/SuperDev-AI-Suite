"""Communication engine: canais, mensagens e notificações.

Estrutura corporativa: canais #geral, #vendas-app, #ia-agents, com
humanos e agentes de IA trocando mensagens, DMs e notificações.
"""

from __future__ import annotations

from typing import Any

from collaboration.collaboration_config import CollaborationConfig
from collaboration.collaboration_events import (CollaborationEventType,
                                                CollaborationEvents)
from collaboration.collaboration_logger import get_logger
from collaboration.collaboration_metrics import CollaborationMetrics
from collaboration.collaboration_models import (ChannelKind, ChannelRecord,
                                                MessageKind, MessageRecord)
from collaboration.collaboration_registry import CollaborationRegistry
from collaboration.collaboration_security import CollaborationSecurity
from collaboration.communication.announcements import AnnouncementManager
from collaboration.communication.channel_manager import ChannelManager
from collaboration.communication.direct_messages import DirectMessageManager
from collaboration.communication.message_manager import MessageManager
from collaboration.communication.notifications import NotificationManager


class CommunicationEngine:
    """Orquestrador de comunicação (Fase 5 do Volume 26)."""

    def __init__(self, events: CollaborationEvents | None = None,
                 metrics: CollaborationMetrics | None = None,
                 config: CollaborationConfig | None = None,
                 security: CollaborationSecurity | None = None,
                 registry: CollaborationRegistry | None = None,
                 channels: ChannelManager | None = None,
                 messages: MessageManager | None = None) -> None:
        self._log = get_logger()
        self.events = events or CollaborationEvents()
        self.metrics = metrics or CollaborationMetrics()
        self.config = config or CollaborationConfig()
        self.security = security or CollaborationSecurity()
        self.channels = channels or ChannelManager(registry=registry)
        self.messages = messages or MessageManager(registry=registry)
        self.direct = DirectMessageManager()
        self.notifications = NotificationManager()
        self.announcements = AnnouncementManager(registry=registry)

    def create_channel(self, workspace_id: str, name: str,
                       topic: str = "",
                       kind: ChannelKind = ChannelKind.CHANNEL,
                       members: list[str] | None = None) -> ChannelRecord:
        channel = self.channels.create(workspace_id, name, topic, kind)
        for member_id in members or []:
            self.channels.join(channel.channel_id, member_id)
        self.metrics.increment("collab.channels")
        return channel

    def get_channel(self, channel_id: str) -> ChannelRecord | None:
        return self.channels.get(channel_id)

    def list_channels(self) -> list[str]:
        return self.channels.list()

    def channels_in(self, workspace_id: str) -> list[ChannelRecord]:
        return self.channels.by_workspace(workspace_id)

    def join(self, channel_id: str, member_id: str) -> ChannelRecord | None:
        return self.channels.join(channel_id, member_id)

    def leave(self, channel_id: str, member_id: str) -> ChannelRecord | None:
        return self.channels.leave(channel_id, member_id)

    def send(self, channel_id: str, author_id: str, body: str,
             kind: MessageKind = MessageKind.CHAT,
             mentions: list[str] | None = None) -> MessageRecord | None:
        message = self.messages.send(channel_id, author_id, body, kind,
                                     mentions)
        if message is not None:
            self.metrics.increment("collab.messages")
            self.events.publish(CollaborationEventType.MESSAGE_SENT,
                                {"message_id": message.message_id,
                                 "channel_id": channel_id,
                                 "author_id": author_id})
        return message

    def messages_for(self, channel_id: str) -> list[MessageRecord]:
        return self.messages.messages_for(channel_id)

    def send_dm(self, sender_id: str, recipient_id: str,
                body: str):
        return self.direct.send(sender_id, recipient_id, body)

    def dm_thread(self, member_a: str, member_b: str):
        return self.direct.thread(member_a, member_b)

    def unread_dms(self, member_id: str):
        return self.direct.unread_for(member_id)

    def notify(self, recipient_id: str, kind: str, title: str,
               body: str = "", reference_id: str = ""):
        return self.notifications.notify(recipient_id, kind, title,
                                         body, reference_id)

    def notifications_for(self, recipient_id: str):
        return self.notifications.for_recipient(recipient_id)

    def unread_notifications(self, recipient_id: str):
        return self.notifications.unread(recipient_id)

    def mark_notification_read(self, notification_id: str) -> None:
        self.notifications.mark_read(notification_id)

    def announce(self, workspace_id: str, title: str, body: str,
                 author_id: str, channel_id: str = "",
                 target: str = "workspace"):
        return self.announcements.announce(workspace_id, title, body,
                                           author_id, channel_id, target)

    def announcements_list(self, workspace_id: str | None = None):
        return self.announcements.list(workspace_id)

    def stats(self) -> dict[str, Any]:
        return {"channels": self.channels.count(),
                "messages": self.messages.count(),
                "direct": self.direct.count(),
                "notifications": self.notifications.count(),
                "announcements": self.announcements.count()}
