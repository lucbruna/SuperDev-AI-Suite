"""
Conversation Manager - Manage conversation state and history.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..customer_context import CustomerContext
from ..customer_events import CustomerEventBus
from ..customer_models import Conversation, Message, ChannelType
from ..customer_config import CustomerConfig

logger = logging.getLogger(__name__)


class ConversationManager:
    def __init__(self, config: CustomerConfig, context: CustomerContext, event_bus: CustomerEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self._conversations: Dict[str, Conversation] = {}
        self._customer_conversations: Dict[str, List[str]] = {}

    def get_or_create(self, customer_id: str, channel: ChannelType = ChannelType.CHAT) -> Conversation:
        customer_convs = self._customer_conversations.get(customer_id, [])
        for conv_id in reversed(customer_convs):
            conv = self._conversations.get(conv_id)
            if conv and conv.status == "active":
                return conv
        conv = Conversation(
            id=str(uuid.uuid4()),
            customer_id=customer_id,
            channel=channel,
        )
        self._conversations[conv.id] = conv
        if customer_id not in self._customer_conversations:
            self._customer_conversations[customer_id] = []
        self._customer_conversations[customer_id].append(conv.id)
        return conv

    def get(self, conversation_id: str) -> Optional[Conversation]:
        return self._conversations.get(conversation_id)

    def save(self, conversation: Conversation) -> None:
        self._conversations[conversation.id] = conversation

    def end_conversation(self, conversation_id: str, satisfaction: float = 0.0) -> bool:
        conv = self._conversations.get(conversation_id)
        if not conv:
            return False
        conv.status = "ended"
        conv.ended_at = datetime.utcnow()
        conv.satisfaction_score = satisfaction
        return True

    def get_history(self, customer_id: str, limit: int = 10) -> List[Conversation]:
        conv_ids = self._customer_conversations.get(customer_id, [])
        result = []
        for cid in reversed(conv_ids):
            conv = self._conversations.get(cid)
            if conv:
                result.append(conv)
            if len(result) >= limit:
                break
        return result

    def get_active_count(self) -> int:
        return sum(1 for c in self._conversations.values() if c.status == "active")
