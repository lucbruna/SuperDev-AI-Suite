"""
Social Connector - Handle social media customer interactions.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..customer_context import CustomerContext
from ..customer_events import CustomerEventBus
from ..customer_config import CustomerConfig

logger = logging.getLogger(__name__)


class SocialConnector:
    def __init__(self, config: CustomerConfig, context: CustomerContext, event_bus: CustomerEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self._platforms = ["instagram", "facebook", "twitter", "linkedin"]

    async def send(self, customer_id: str, message: str, platform: str = "instagram") -> Dict[str, Any]:
        return {
            "channel": "social",
            "platform": platform,
            "to": customer_id,
            "message_id": str(uuid.uuid4()),
            "status": "published",
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def monitor_mentions(self) -> List[Dict[str, Any]]:
        return [
            {"platform": "twitter", "mention": "@empresa", "sentiment": "neutral", "text": "Exemplo de menção"},
        ]

    def get_supported_platforms(self) -> List[str]:
        return self._platforms.copy()
