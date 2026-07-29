"""
Trigger Manager - Define and manage event-based automation triggers.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any, Callable, Dict, List, Optional

from ..customer_context import CustomerContext
from ..customer_events import CustomerEventBus
from ..customer_config import CustomerConfig

logger = logging.getLogger(__name__)


class TriggerManager:
    def __init__(self, config: CustomerConfig, context: CustomerContext, event_bus: CustomerEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self._triggers: Dict[str, Dict[str, Any]] = {}

    def register(self, name: str, event_type: str, action: str, params: Optional[Dict] = None) -> str:
        trigger_id = str(uuid.uuid4())
        self._triggers[trigger_id] = {
            "id": trigger_id,
            "name": name,
            "event_type": event_type,
            "action": action,
            "params": params or {},
            "active": True,
        }
        logger.info(f"Trigger registered: {name} -> {action}")
        return trigger_id

    def activate(self, trigger_id: str) -> bool:
        trigger = self._triggers.get(trigger_id)
        if not trigger:
            return False
        trigger["active"] = True
        return True

    def deactivate(self, trigger_id: str) -> bool:
        trigger = self._triggers.get(trigger_id)
        if not trigger:
            return False
        trigger["active"] = False
        return True

    def list_active(self) -> List[Dict[str, Any]]:
        return [t for t in self._triggers.values() if t["active"]]

    def get_default_triggers(self) -> List[Dict[str, Any]]:
        return [
            {"name": "new_customer_welcome", "event": "customer.created", "action": "send_welcome_email"},
            {"name": "cart_abandonment", "event": "cart.abandoned", "action": "send_cart_reminder"},
            {"name": "inactive_30_days", "event": "customer.inactive", "action": "send_reengagement"},
            {"name": "high_value_purchase", "event": "purchase.completed", "action": "send_thank_you"},
        ]
