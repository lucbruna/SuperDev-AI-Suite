"""Mobile Events - Event-driven messaging for mobile/edge platform."""
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import hashlib


class MobileEventType(Enum):
    DEVICE_CONNECTED = "device_connected"
    DEVICE_DISCONNECTED = "device_disconnected"
    SYNC_STARTED = "sync_started"
    SYNC_COMPLETED = "sync_completed"
    SYNC_FAILED = "sync_failed"
    MODEL_LOADED = "model_loaded"
    INFERENCE_COMPLETE = "inference_complete"
    OFFLINE_MODE_ENTERED = "offline_mode_entered"
    OFFLINE_MODE_EXITED = "offline_mode_exited"
    SECURITY_ALERT = "security_alert"
    NOTIFICATION_SENT = "notification_sent"
    BIOMETRIC_AUTH = "biometric_auth"
    UPDATE_AVAILABLE = "update_available"


@dataclass
class MobileEvent:
    event_id: str
    event_type: MobileEventType
    device_id: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class MobileEventBus:
    def __init__(self):
        self.events: List[MobileEvent] = []
        self.subscribers: Dict[MobileEventType, List[Callable]] = {}

    def publish(self, event_type: MobileEventType, device_id: str, data: Dict[str, Any] = None) -> MobileEvent:
        event_id = hashlib.sha256(f"{event_type.value}{device_id}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        event = MobileEvent(event_id=event_id, event_type=event_type, device_id=device_id, data=data or {})
        self.events.append(event)
        for handler in self.subscribers.get(event_type, []):
            try:
                handler(event)
            except Exception:
                pass
        return event

    def subscribe(self, event_type: MobileEventType, handler: Callable) -> None:
        self.subscribers.setdefault(event_type, []).append(handler)

    def unsubscribe(self, event_type: MobileEventType, handler: Callable) -> bool:
        if event_type in self.subscribers:
            try:
                self.subscribers[event_type].remove(handler)
                return True
            except ValueError:
                pass
        return False

    def get_events(self, event_type: MobileEventType = None, device_id: str = None, limit: int = 100) -> List[MobileEvent]:
        events = self.events
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        if device_id:
            events = [e for e in events if e.device_id == device_id]
        return events[-limit:]

    def count(self) -> int:
        return len(self.events)
