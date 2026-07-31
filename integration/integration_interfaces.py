from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Protocol, runtime_checkable

from .integration_models import ConnectionConfig, EventMessage, MessageRecord


class Connector(ABC):
    """Contract for connectors to external systems."""

    @abstractmethod
    def connect(self, config: ConnectionConfig) -> bool: ...

    @abstractmethod
    def disconnect(self) -> bool: ...

    @abstractmethod
    def invoke(self, operation: str, params: dict[str, Any] | None = None) -> Any: ...

    @abstractmethod
    def test(self) -> bool: ...

    @abstractmethod
    def status(self) -> str: ...

    @abstractmethod
    def is_connected(self) -> bool: ...


class AuthProvider(ABC):
    """Contract for authentication providers (oauth, jwt, api key)."""

    @abstractmethod
    def authenticate(self, credentials: dict[str, Any]) -> str: ...

    @abstractmethod
    def validate(self, token: str) -> bool: ...

    @abstractmethod
    def revoke(self, token: str) -> bool: ...


class Transformer(ABC):
    """Contract for data transformation between systems."""

    @abstractmethod
    def transform(self, data: Any, **options: Any) -> Any: ...


class MessageBroker(ABC):
    """Contract for messaging brokers."""

    @abstractmethod
    def publish(self, queue: str, message: MessageRecord) -> str: ...

    @abstractmethod
    def subscribe(self, queue: str, handler: Any) -> None: ...

    @abstractmethod
    def consume(self, queue: str) -> MessageRecord | None: ...

    @abstractmethod
    def count(self, queue: str) -> int: ...


@runtime_checkable
class WebhookHandler(Protocol):
    """Anything that can handle a webhook delivery."""

    def handle(self, event_type: str, payload: dict[str, Any]) -> Any: ...


@runtime_checkable
class EventSubscriber(Protocol):
    """Anything that subscribes to integration events."""

    def on_event(self, message: EventMessage) -> None: ...
