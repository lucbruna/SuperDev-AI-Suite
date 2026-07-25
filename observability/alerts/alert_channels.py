import json
import urllib.request
import urllib.error
from abc import ABC, abstractmethod
from typing import Any, Dict


class AlertChannel(ABC):
    @abstractmethod
    def send(self, alert: Dict[str, Any]) -> bool:
        ...


class SlackChannel(AlertChannel):
    def __init__(self, webhook_url: str) -> None:
        self._webhook_url = webhook_url

    def send(self, alert: Dict[str, Any]) -> bool:
        try:
            payload = json.dumps({
                "text": f"[{alert.get('severity', 'INFO').upper()}] {alert.get('name', 'Alert')}: {alert.get('message', '')}"
            }).encode("utf-8")
            req = urllib.request.Request(
                self._webhook_url,
                data=payload,
                headers={"Content-Type": "application/json"},
            )
            urllib.request.urlopen(req, timeout=10)
            return True
        except (urllib.error.URLError, OSError):
            return False


class WebhookChannel(AlertChannel):
    def __init__(self, url: str) -> None:
        self._url = url

    def send(self, alert: Dict[str, Any]) -> bool:
        try:
            payload = json.dumps(alert).encode("utf-8")
            req = urllib.request.Request(
                self._url,
                data=payload,
                headers={"Content-Type": "application/json"},
            )
            urllib.request.urlopen(req, timeout=10)
            return True
        except (urllib.error.URLError, OSError):
            return False


class ConsoleChannel(AlertChannel):
    def send(self, alert: Dict[str, Any]) -> bool:
        print(f"ALERT: {alert.get('severity', 'INFO').upper()} | {alert.get('name', 'Alert')} | {alert.get('message', '')}")
        return True
