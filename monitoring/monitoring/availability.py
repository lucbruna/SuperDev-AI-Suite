import time
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class AvailabilityEvent:
    service: str
    up: bool
    timestamp: float


class AvailabilityMonitor:
    def __init__(self) -> None:
        self._events: Dict[str, List[AvailabilityEvent]] = {}

    def record_event(self, service: str, up: bool = True) -> None:
        if service not in self._events:
            self._events[service] = []
        self._events[service].append(AvailabilityEvent(service=service, up=up, timestamp=time.time()))

    def get_uptime(self, service: str, period_days: float = 7.0) -> float:
        events = self._events.get(service, [])
        cutoff = time.time() - (period_days * 86400)
        filtered = [e for e in events if e.timestamp >= cutoff]
        if not filtered:
            return 100.0
        up_count = sum(1 for e in filtered if e.up)
        return (up_count / len(filtered)) * 100.0

    def get_downtime_events(self, service: str) -> List[AvailabilityEvent]:
        events = self._events.get(service, [])
        return [e for e in events if not e.up]

    def get_all_events(self, service: str) -> List[AvailabilityEvent]:
        return list(self._events.get(service, []))
