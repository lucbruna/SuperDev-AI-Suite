from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


class ConnectorStatus(str, Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


class MessageStatus(str, Enum):
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"


class SyncStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ConnectionConfig:
    """Configuration for a connection to an external system."""

    name: str
    connector_type: str
    config: dict[str, Any] = field(default_factory=dict)
    auth_method: str = "none"
    credentials_ref: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "connector_type": self.connector_type,
            "config": dict(self.config),
            "auth_method": self.auth_method,
            "credentials_ref": self.credentials_ref,
            "metadata": dict(self.metadata),
            "created_at": self.created_at,
        }


@dataclass
class ConnectionRecord:
    """A persisted connection with runtime status."""

    connection_id: str
    config: ConnectionConfig
    status: ConnectorStatus = ConnectorStatus.DISCONNECTED
    connected_at: str = ""
    error: str = ""
    updated_at: str = field(default_factory=_utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "connection_id": self.connection_id,
            "config": self.config.to_dict(),
            "status": self.status.value,
            "connected_at": self.connected_at,
            "error": self.error,
            "updated_at": self.updated_at,
        }


@dataclass
class APIEndpoint:
    """A registered API endpoint exposed by the gateway."""

    method: str
    path: str
    operation: str
    version: str = "v1"
    auth_required: bool = True
    rate_limit: int = 0
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "path": self.path,
            "operation": self.operation,
            "version": self.version,
            "auth_required": self.auth_required,
            "rate_limit": self.rate_limit,
            "description": self.description,
            "metadata": dict(self.metadata),
        }


@dataclass
class IntegrationDefinition:
    """Metadata describing a reusable integration."""

    integration_id: str
    name: str
    category: str = "generic"
    provider: str = "custom"
    version: str = "1.0.0"
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "integration_id": self.integration_id,
            "name": self.name,
            "category": self.category,
            "provider": self.provider,
            "version": self.version,
            "description": self.description,
            "metadata": dict(self.metadata),
        }


@dataclass
class WebhookRecord:
    """A webhook registration with delivery metadata."""

    webhook_id: str
    url: str
    events: list[str] = field(default_factory=list)
    secret: str = ""
    enabled: bool = True
    created_at: str = field(default_factory=_utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "webhook_id": self.webhook_id,
            "url": self.url,
            "events": list(self.events),
            "enabled": self.enabled,
            "created_at": self.created_at,
            "metadata": dict(self.metadata),
        }


@dataclass
class EventMessage:
    """An internal event message flowing through the event bus."""

    event_type: str
    payload: dict[str, Any] = field(default_factory=dict)
    source: str = "integration"
    correlation_id: str = ""
    timestamp: str = field(default_factory=_utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "payload": dict(self.payload),
            "source": self.source,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp,
        }


@dataclass
class MessageRecord:
    """A message in a messaging queue."""

    queue: str
    payload: dict[str, Any] = field(default_factory=dict)
    message_id: str = ""
    priority: int = 0
    status: MessageStatus = MessageStatus.PENDING
    created_at: str = field(default_factory=_utcnow)
    attempts: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "queue": self.queue,
            "payload": dict(self.payload),
            "message_id": self.message_id,
            "priority": self.priority,
            "status": self.status.value,
            "created_at": self.created_at,
            "attempts": self.attempts,
        }


@dataclass
class SyncRecord:
    """A record of a synchronization operation."""

    sync_id: str
    connection_id: str
    direction: str = "pull"
    status: SyncStatus = SyncStatus.PENDING
    records_processed: int = 0
    records_failed: int = 0
    started_at: str = field(default_factory=_utcnow)
    finished_at: str = ""
    error: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "sync_id": self.sync_id,
            "connection_id": self.connection_id,
            "direction": self.direction,
            "status": self.status.value,
            "records_processed": self.records_processed,
            "records_failed": self.records_failed,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "error": self.error,
        }


@dataclass
class HealthReport:
    """A health check result for a connection or component."""

    component: str
    status: str = "ok"
    latency_ms: float = 0.0
    last_checked_at: str = field(default_factory=_utcnow)
    message: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "component": self.component,
            "status": self.status,
            "latency_ms": self.latency_ms,
            "last_checked_at": self.last_checked_at,
            "message": self.message,
            "metadata": dict(self.metadata),
        }


@dataclass
class MonitorAlert:
    """An alert raised by the monitoring subsystem."""

    alert_id: str
    severity: str = "warning"
    source: str = "monitoring"
    message: str = ""
    timestamp: str = field(default_factory=_utcnow)
    resolved: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "severity": self.severity,
            "source": self.source,
            "message": self.message,
            "timestamp": self.timestamp,
            "resolved": self.resolved,
            "metadata": dict(self.metadata),
        }
