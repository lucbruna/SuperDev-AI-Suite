from __future__ import annotations

import time
from typing import Any, Dict, List, Optional


class DistributedCache:
    """Simulated distributed cache node."""

    def __init__(self, node_id: str, sync_interval: float = 60.0) -> None:
        self._node_id = node_id
        self._sync_interval = sync_interval
        self._data: Dict[str, Any] = {}
        self._timestamps: Dict[str, float] = {}
        self._last_sync: float = time.time()

    @property
    def node_id(self) -> str:
        return self._node_id

    @property
    def size(self) -> int:
        return len(self._data)

    @property
    def last_sync(self) -> float:
        return self._last_sync

    def get(self, key: str) -> Optional[Any]:
        return self._data.get(key)

    def set(self, key: str, value: Any, ttl: float = 300.0) -> None:
        self._data[key] = value
        self._timestamps[key] = time.time()

    def delete(self, key: str) -> bool:
        if key in self._data:
            del self._data[key]
            self._timestamps.pop(key, None)
            return True
        return False

    def clear(self) -> None:
        self._data.clear()
        self._timestamps.clear()

    def sync(self, peer: "DistributedCache") -> int:
        synced = 0
        for key in peer.keys():
            if key not in self._data or peer._timestamps.get(key, 0) >= self._timestamps.get(key, 0):
                self._data[key] = peer.get(key)
                self._timestamps[key] = peer._timestamps.get(key, 0)
                synced += 1
        self._last_sync = time.time()
        return synced

    def keys(self) -> List[str]:
        return list(self._data.keys())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self._node_id,
            "size": self.size,
            "last_sync": self._last_sync,
        }
