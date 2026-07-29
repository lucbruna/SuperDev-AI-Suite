"""
Chatbot Engine - Core conversational intelligence coordination.

Manages real conversation flows, intent routing, and response generation.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..customer_context import CustomerContext
from ..customer_events import CustomerEvent, CustomerEventBus, EventType
from ..customer_models import Conversation, Message, ChannelType
from ..customer_config import CustomerConfig
from .conversation_manager import ConversationManager
from .intent_classifier import IntentClassifier
from .response_generator import ResponseGenerator
from .knowledge_connector import KnowledgeConnector

logger = logging.getLogger(__name__)


class ChatbotEngine:
    def __init__(self, config: CustomerConfig, context: CustomerContext, event_bus: CustomerEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self.conversations: Optional[ConversationManager] = None
        self.classifier: Optional[IntentClassifier] = None
        self.generator: Optional[ResponseGenerator] = None
        self.knowledge: Optional[KnowledgeConnector] = None

    async def initialize(self) -> None:
        self.conversations = ConversationManager(self.config, self.context, self.event_bus)
        self.classifier = IntentClassifier(self.config, self.context, self.event_bus)
        self.generator = ResponseGenerator(self.config, self.context, self.event_bus)
        self.knowledge = KnowledgeConnector(self.config, self.context, self.event_bus)
        logger.info("ChatbotEngine initialized")

    async def process(self, customer_id: str, message_text: str, channel: ChannelType = ChannelType.CHAT) -> Conversation:
        conv = self.conversations.get_or_create(customer_id, channel)
        msg = Message(
            id=str(uuid.uuid4()),
            content=message_text,
            sender="customer",
            channel=channel,
        )
        conv.messages.append(msg)
        intent = self.classifier.classify(message_text)
        conv.intent = intent
        response_text = self.generator.generate(intent, message_text, conv)
        if response_text:
            reply = Message(
                id=str(uuid.uuid4()),
                content=response_text,
                sender="bot",
                channel=channel,
            )
            conv.messages.append(reply)
        await self.event_bus.publish(CustomerEvent(
            event_type=EventType.MESSAGE_RECEIVED,
            payload={"customer_id": customer_id, "intent": intent, "message": message_text},
        ))
        self.conversations.save(conv)
        logger.info(f"Processed message from {customer_id}: intent={intent}")
        return conv

    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        return self.conversations.get(conversation_id)

    async def shutdown(self) -> None:
        logger.info("ChatbotEngine shutdown")
