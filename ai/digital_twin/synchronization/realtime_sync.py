"""Realtime sync."""
from __future__ import annotations
from typing import Any, Callable, Dict, List
import time

class RealtimeSync:
    def __init__(self) -> None:
        self._channels: Dict[str, List[Callable]] = {}
        self._buffer: List[Dict[str, Any]] = []
        self._started = False
    def start(self) -> None:
        self._started = True
    def subscribe(self, channel: str, callback: Callable) -> None:
        self._channels.setdefault(channel, []).append(callback)
    def publish(self, channel: str, data: Any) -> int:
        count = 0
        for callback in self._channels.get(channel, []):
            try:
                callback(data)
                count += 1
            except Exception:
                pass
        self._buffer.append({"channel": channel, "data": data, "timestamp": time.time()})
        return count
    def buffer_size(self) -> int:
        return len(self._buffer)
    def flush(self) -> List[Dict[str, Any]]:
        flushed = self._buffer[:]
        self._buffer.clear()
        return flushed
    def list_channels(self) -> List[str]:
        return list(self._channels.keys())
    def subscriber_count(self, channel: str = "") -> int:
        if channel:
            return len(self._channels.get(channel, []))
        return sum(len(v) for v in self._channels.values())
    def is_running(self) -> bool:
        return self._started
