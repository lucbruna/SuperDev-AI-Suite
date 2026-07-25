import time
from typing import Dict, List


class HeartbeatMonitor:
    def __init__(self) -> None:
        self._heartbeats: Dict[str, float] = {}

    def beat(self, service_id: str, ttl_seconds: float = 30.0) -> None:
        self._heartbeats[service_id] = time.time()

    def is_alive(self, service_id: str, ttl_seconds: float = 30.0) -> bool:
        timestamp = self._heartbeats.get(service_id)
        if timestamp is None:
            return False
        return (time.time() - timestamp) < ttl_seconds

    def get_dead_services(self, ttl_seconds: float = 30.0) -> List[str]:
        now = time.time()
        return [
            sid for sid, ts in self._heartbeats.items()
            if (now - ts) >= ttl_seconds
        ]

    def get_all(self) -> Dict[str, float]:
        return dict(self._heartbeats)
