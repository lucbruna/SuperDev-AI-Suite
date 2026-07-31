"""ERP Events — Event-driven messaging for ERP operations."""
import contextlib
import hashlib
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ERPEventType(Enum):
    PRODUCT_CREATED = "product_created"
    STOCK_UPDATED = "stock_updated"
    ORDER_CREATED = "order_created"
    ORDER_SHIPPED = "order_shipped"
    PURCHASE_APPROVED = "purchase_approved"
    DELIVERY_COMPLETED = "delivery_completed"
    WORK_ORDER_STARTED = "work_order_started"
    LOW_STOCK_DETECTED = "low_stock_detected"
    WORKFLOW_SUBMITTED = "workflow_submitted"


@dataclass
class ERPEvent:
    event_id: str
    event_type: ERPEventType
    source: str
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class ERPEventBus:
    def __init__(self):
        self.events: list[ERPEvent] = []
        self.subscribers: dict[ERPEventType, list[Callable]] = {}

    def publish(self, event_type: ERPEventType, source: str, data: dict[str, Any] | None = None) -> ERPEvent:
        event_id = hashlib.sha256(f"{event_type.value}{source}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        event = ERPEvent(event_id=event_id, event_type=event_type, source=source, data=data or {})
        self.events.append(event)
        for handler in self.subscribers.get(event_type, []):
            with contextlib.suppress(Exception):
                handler(event)
        return event

    def subscribe(self, event_type: ERPEventType, handler: Callable) -> None:
        self.subscribers.setdefault(event_type, []).append(handler)

    def get_events(self, event_type: ERPEventType | None = None, source: str | None = None, limit: int = 100) -> list[ERPEvent]:
        events = self.events
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        if source:
            events = [e for e in events if e.source == source]
        return events[-limit:]

    def count(self) -> int:
        return len(self.events)
