"""
Behavior Analysis - Track and analyze customer behavior patterns.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..customer_context import CustomerContext
from ..customer_events import CustomerEvent, CustomerEventBus, EventType
from ..customer_config import CustomerConfig

logger = logging.getLogger(__name__)


class BehaviorAnalysis:
    def __init__(self, config: CustomerConfig, context: CustomerContext, event_bus: CustomerEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self._events: Dict[str, List[Dict[str, Any]]] = {}

    def track(self, customer_id: str, event_type: str, data: Dict[str, Any]) -> None:
        if customer_id not in self._events:
            self._events[customer_id] = []
        self._events[customer_id].append({
            "type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
        })
        logger.info(f"Behavior tracked: {customer_id} -> {event_type}")

    def get_frequencies(self, customer_id: str) -> Dict[str, int]:
        freq = {}
        for event in self._events.get(customer_id, []):
            event_type = event["type"]
            freq[event_type] = freq.get(event_type, 0) + 1
        return freq

    def get_last_activity(self, customer_id: str) -> Optional[str]:
        events = self._events.get(customer_id, [])
        if not events:
            return None
        return events[-1]["type"]

    def get_active_hours(self, customer_id: str) -> List[int]:
        hours = []
        for event in self._events.get(customer_id, []):
            ts = datetime.fromisoformat(event["timestamp"])
            hours.append(ts.hour)
        return hours

    def get_viewed_categories(self, customer_id: str) -> List[str]:
        categories = set()
        for event in self._events.get(customer_id, []):
            if event["type"] == "view_product":
                cat = event["data"].get("category", "")
                if cat:
                    categories.add(cat)
        return list(categories)

    def get_purchase_history(self, customer_id: str) -> List[str]:
        products = []
        for event in self._events.get(customer_id, []):
            if event["type"] == "purchase":
                items = event["data"].get("items", [])
                products.extend(items)
        return products
