"""Communication subsystem (Volume 26, Fase 5): canais e mensagens.

CommunicationEngine gerencia canais, mensagens (incluindo de agentes IA),
mensagens diretas, notificações e anúncios.
"""
from __future__ import annotations

from .announcements import Announcement, AnnouncementManager
from .channel_manager import ChannelManager
from .communication_engine import CommunicationEngine
from .direct_messages import DirectMessage, DirectMessageManager
from .message_manager import MessageManager
from .notifications import Notification, NotificationManager

__all__ = [
    "Announcement",
    "AnnouncementManager",
    "ChannelManager",
    "CommunicationEngine",
    "DirectMessage",
    "DirectMessageManager",
    "MessageManager",
    "Notification",
    "NotificationManager",
]
