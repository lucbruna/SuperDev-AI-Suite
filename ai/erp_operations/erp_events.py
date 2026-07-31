"""ERP Events — Event-driven messaging for ERP operations."""
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import hashlib


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
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class ERPEventBus:
    def __init__(self):
        self.events: List[ERPEvent] = []
        self.subscribers: Dict[ERPEventType, List[Callable]] = {}

    def publish(self, event_type: ERPEventType, source: str, data: Optional[Dict[str, Any]] = None) -> ERPEvent:
        event_id = hashlib.sha256(f"{event_type.value}{source}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        event = ERPEvent(event_id=event_id, event_type=event_type, source=source, data=data or {})
        self.events.append(event)
        for handler in self.subscribers.get(event_type, []):
            try:
                handler(event)
            except Exception:
                pass
        return event

    def subscribe(self, event_type: ERPEventType, handler: Callable) -> None:
        self.subscribers.setdefault(event_type, []).append(handler)

    def get_events(self, event_type: Optional[ERPEventType] = None, source: Optional[str] = None, limit: int = 100) -> List[ERPEvent]:
        events = self.events
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        if source:
            events = [e for e in events if e.source == source]
        return events[-limit:]

    def count(self) -> int:
        return len(self.events)
