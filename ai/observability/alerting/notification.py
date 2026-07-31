"""Alert notifications."""
from __future__ import annotations
from typing import Any, Callable, Dict, List

class AlertNotifier:
    def __init__(self) -> None:
        self._channels: Dict[str, Callable[[Dict[str, Any]], bool]] = {}
        self._history: List[Dict[str, Any]] = []
    def add_channel(self, name: str, handler: Callable[[Dict[str, Any]], bool]) -> None:
        self._channels[name] = handler
    def remove_channel(self, name: str) -> bool:
        if name in self._channels:
            del self._channels[name]
            return True
        return False
    def notify(self, alert: Dict[str, Any], channels: List[str] = None) -> Dict[str, bool]:
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
    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._history[-limit:]
    def list_channels(self) -> List[str]:
        return list(self._channels.keys())
