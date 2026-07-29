"""
Omnichannel Engine - Unify all customer communication channels.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..customer_context import CustomerContext
from ..customer_events import CustomerEvent, CustomerEventBus, EventType
from ..customer_models import ChannelType
from ..customer_config import CustomerConfig
from .channel_manager import ChannelManager
from .whatsapp_connector import WhatsAppConnector
from .email_connector import EmailConnector
from .webchat_connector import WebchatConnector
from .social_connector import SocialConnector

logger = logging.getLogger(__name__)


class OmnichannelEngine:
    def __init__(self, config: CustomerConfig, context: CustomerContext, event_bus: CustomerEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self.channels: Optional[ChannelManager] = None
        self.whatsapp: Optional[WhatsAppConnector] = None
        self.email: Optional[EmailConnector] = None
        self.webchat: Optional[WebchatConnector] = None
        self.social: Optional[SocialConnector] = None

    async def initialize(self) -> None:
        self.channels = ChannelManager(self.config, self.context, self.event_bus)
        self.whatsapp = WhatsAppConnector(self.config, self.context, self.event_bus)
        self.email = EmailConnector(self.config, self.context, self.event_bus)
        self.webchat = WebchatConnector(self.config, self.context, self.event_bus)
        self.social = SocialConnector(self.config, self.context, self.event_bus)
        logger.info("OmnichannelEngine initialized")

    async def route_message(self, channel: ChannelType, customer_id: str, message: str) -> Dict[str, Any]:
        if channel == ChannelType.WHATSAPP:
            result = await self.whatsapp.send(customer_id, message)
        elif channel == ChannelType.EMAIL:
            result = await self.email.send(customer_id, message)
        elif channel == ChannelType.WEBSITE:
            result = await self.webchat.send(customer_id, message)
        elif channel == ChannelType.SOCIAL:
            result = await self.social.send(customer_id, message)
        else:
            result = {"status": "unsupported_channel"}
        self.channels.log_interaction(customer_id, channel, message)
        return result

    async def shutdown(self) -> None:
        logger.info("OmnichannelEngine shutdown")
