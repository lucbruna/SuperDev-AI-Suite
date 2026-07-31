from __future__ import annotations

from typing import Any, Callable, Protocol, runtime_checkable

from .integration_models import ConnectionConfig, IntegrationDefinition


@runtime_checkable
class ConnectorLike(Protocol):
    """Protocol for connector-compatible objects."""

    def connect(self, config: ConnectionConfig) -> bool: ...

    def disconnect(self) -> bool: ...

    def invoke(self, operation: str, params: dict[str, Any] | None = None) -> Any: ...

    def test(self) -> bool: ...

    def is_connected(self) -> bool: ...


@runtime_checkable
class AuthLike(Protocol):
    """Protocol for authentication providers."""

    def authenticate(self, credentials: dict[str, Any]) -> str: ...

    def validate(self, token: str) -> bool: ...


@runtime_checkable
class TransformLike(Protocol):
    """Protocol for transformers."""

    def transform(self, data: Any, **options: Any) -> Any: ...


@runtime_checkable
class WebhookLike(Protocol):
    """Protocol for webhook receivers/senders."""

    def handle(self, event_type: str, payload: dict[str, Any]) -> Any: ...


@runtime_checkable
class SchedulerLike(Protocol):
    """Protocol for sync schedulers."""

    def schedule(self, interval: int, job: Callable[..., Any]) -> None: ...


@runtime_checkable
class HealthProbe(Protocol):
    """Protocol for health check probes."""

    def probe(self) -> dict[str, Any]: ...


@runtime_checkable
class MarketplaceItem(Protocol):
    """Protocol for marketplace integration items."""

    def to_dict(self) -> dict[str, Any]: ...


Callback = Callable[..., Any]
