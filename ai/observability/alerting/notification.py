"""Alert notifications."""
from __future__ import annotations

from collections.abc import Callable
from typing import Any


class AlertNotifier:
    def __init__(self) -> None:
        self._channels: dict[str, Callable[[dict[str, Any]], bool]] = {}
        self._history: list[dict[str, Any]] = []
    def add_channel(self, name: str, handler: Callable[[dict[str, Any]], bool]) -> None:
        self._channels[name] = handler
    def remove_channel(self, name: str) -> bool:
        if name in self._channels:
            del self._channels[name]
            return True
        return False
    def notify(self, alert: dict[str, Any], channels: list[str] = None) -> dict[str, bool]:
        target_channels = channels or list(self._channels.keys())
        results = {}
        for ch in target_channels:
            handler = self._channels.get(ch)
            if handler:
                try:
                    results[ch] = handler(alert)
                except Exception:
                    results[ch] = False
            else:
                results[ch] = False
        self._history.append({"alert": alert, "channels": target_channels, "results": results})
        return results
    def get_history(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._history[-limit:]
    def list_channels(self) -> list[str]:
        return list(self._channels.keys())
