"""
Channel Manager - Track channel interactions and unify customer context.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..customer_context import CustomerContext
from ..customer_events import CustomerEvent, CustomerEventBus, EventType
from ..customer_models import ChannelType
from ..customer_config import CustomerConfig

logger = logging.getLogger(__name__)


class ChannelManager:
    def __init__(self, config: CustomerConfig, context: CustomerContext, event_bus: CustomerEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self._interactions: Dict[str, List[Dict[str, Any]]] = {}
        self._channel_map: Dict[str, str] = {}

    def identify_customer(self, external_id: str, channel: ChannelType, customer_id: str) -> None:
        key = f"{channel.value}:{external_id}"
        self._channel_map[key] = customer_id

    def resolve_customer(self, external_id: str, channel: ChannelType) -> Optional[str]:
        key = f"{channel.value}:{external_id}"
        return self._channel_map.get(key)

    def log_interaction(self, customer_id: str, channel: ChannelType, content: str) -> Dict[str, Any]:
        if customer_id not in self._interactions:
            self._interactions[customer_id] = []
        interaction = {
            "id": str(uuid.uuid4()),
            "channel": channel.value,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._interactions[customer_id].append(interaction)
        return interaction

    def get_customer_journey(self, customer_id: str) -> List[Dict[str, Any]]:
        return self._interactions.get(customer_id, [])

    def get_channels_used(self, customer_id: str) -> List[str]:
        channels = set()
        for interaction in self._interactions.get(customer_id, []):
            channels.add(interaction["channel"])
        return list(channels)

    def get_channel_stats(self) -> Dict[str, int]:
        stats = {}
        for customer_id, interactions in self._interactions.items():
            for interaction in interactions:
                ch = interaction["channel"]
                stats[ch] = stats.get(ch, 0) + 1
        return stats
