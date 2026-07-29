"""
Marketing Events - Event system for marketing
"""

from datetime import datetime
from typing import Any, Callable, Dict, List
from uuid import UUID
from collections import defaultdict


class MarketingEventBus:
    """Event bus for marketing events"""

    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._history: List[Dict] = []

    async def publish(self, event_type: str, payload: Dict[str, Any]) -> None:
        event = {
            "type": event_type,
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._history.append(event)

        for handler in self._subscribers.get(event_type, []):
            try:
                await handler(event)
            except Exception:
                pass

        for handler in self._subscribers.get("*", []):
            try:
                await handler(event)
            except Exception:
                pass

    def subscribe(self, event_type: str, handler: Callable) -> None:
        self._subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: Callable) -> bool:
        if handler in self._subscribers[event_type]:
            self._subscribers[event_type].remove(handler)
            return True
        return False

    def get_history(self, event_type: Optional[str] = None, limit: int = 100) -> List[Dict]:
        events = self._history
        if event_type:
            events = [e for e in events if e["type"] == event_type]
        return events[-limit:]