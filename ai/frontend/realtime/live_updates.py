"""
Live Updates Manager
"""

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any


class UpdateType(Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    REFRESH = "refresh"


@dataclass
class LiveUpdate:
    resource: str
    update_type: UpdateType
    data: Any
    id: str = ""


class LiveUpdatesManager:
    def __init__(self):
        self.subscriptions: dict[str, list[Callable]] = {}
        self.buffer: list[LiveUpdate] = []
        self.batch_size: int = 10

    def subscribe(self, resource: str, callback: Callable) -> None:
        if resource not in self.subscriptions:
            self.subscriptions[resource] = []
        self.subscriptions[resource].append(callback)

    def unsubscribe(self, resource: str, callback: Callable) -> None:
        if resource in self.subscriptions:
            self.subscriptions[resource] = [h for h in self.subscriptions[resource] if h != callback]

    def push(self, update: LiveUpdate) -> None:
        self.buffer.append(update)
        if len(self.buffer) >= self.batch_size:
            self.flush()

    def flush(self) -> None:
        for update in self.buffer:
            for handler in self.subscriptions.get(update.resource, []):
                handler(update)
            for handler in self.subscriptions.get("*", []):
                handler(update)
        self.buffer.clear()

    def render(self) -> dict[str, Any]:
        return {"subscriptions": list(self.subscriptions.keys()), "bufferSize": len(self.buffer)}
