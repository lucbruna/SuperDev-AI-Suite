"""
Integration Engine - Core orchestration
"""
import hashlib
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class IntegrationType(Enum):
    API = "api"
    WEBHOOK = "webhook"
    DATABASE = "database"
    FILE = "file"
    MESSAGE_QUEUE = "message_queue"
    FTP = "ftp"
    SOAP = "soap"
    GRAPHQL = "graphql"
    GRPC = "grpc"
    CUSTOM = "custom"


class IntegrationStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    SYNCING = "syncing"
    PAUSED = "paused"


@dataclass
class IntegrationDefinition:
    integration_id: str
    name: str
    integration_type: IntegrationType
    status: IntegrationStatus = IntegrationStatus.INACTIVE
    source_system: str = ""
    target_system: str = ""
    config: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_sync: datetime | None = None
    error_count: int = 0
    tags: list[str] = field(default_factory=list)


@dataclass
class IntegrationResult:
    success: bool
    integration_id: str
    data: Any = None
    error: str = ""
    duration_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


class IntegrationEngine:
    def __init__(self):
        self.integrations: dict[str, IntegrationDefinition] = {}
        self.handlers: dict[str, Callable] = {}
        self.middleware: list[Callable] = []
        self.event_handlers: dict[str, list[Callable]] = {}
        self._hooks: dict[str, list[Callable]] = {
            "before_connect": [], "after_connect": [],
            "before_sync": [], "after_sync": [],
            "on_error": [], "on_success": [],
        }

    def register_integration(self, name: str, integration_type: IntegrationType, **kwargs) -> IntegrationDefinition:
        integration_id = hashlib.sha256(f"{name}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        definition = IntegrationDefinition(integration_id=integration_id, name=name, integration_type=integration_type, **kwargs)
        self.integrations[integration_id] = definition
        return definition

    def get_integration(self, integration_id: str) -> IntegrationDefinition | None:
        return self.integrations.get(integration_id)

    def update_status(self, integration_id: str, status: IntegrationStatus) -> bool:
        integration = self.integrations.get(integration_id)
        if integration:
            integration.status = status
            integration.updated_at = datetime.now()
            return True
        return False

    def register_handler(self, integration_id: str, handler: Callable) -> None:
        self.handlers[integration_id] = handler

    def add_middleware(self, middleware: Callable) -> None:
        self.middleware.append(middleware)

    def add_hook(self, hook_name: str, callback: Callable) -> None:
        if hook_name in self._hooks:
            self._hooks[hook_name].append(callback)

    def trigger_hooks(self, hook_name: str, context: dict[str, Any]) -> None:
        for callback in self._hooks.get(hook_name, []):
            callback(context)

    def execute(self, integration_id: str, data: Any = None) -> IntegrationResult:
        integration = self.integrations.get(integration_id)
        if not integration:
            return IntegrationResult(success=False, integration_id=integration_id, error="Integration not found")
        if integration.status != IntegrationStatus.ACTIVE:
            return IntegrationResult(success=False, integration_id=integration_id, error="Integration not active")
        start = datetime.now()
        try:
            for mw in self.middleware:
                data = mw(data)
            handler = self.handlers.get(integration_id)
            result_data = handler(data) if handler else data
            duration = (datetime.now() - start).total_seconds() * 1000
            integration.last_sync = datetime.now()
            return IntegrationResult(success=True, integration_id=integration_id, data=result_data, duration_ms=duration)
        except Exception as e:
            integration.error_count += 1
            return IntegrationResult(success=False, integration_id=integration_id, error=str(e))

    def list_integrations(self, status: IntegrationStatus = None) -> list[IntegrationDefinition]:
        if status:
            return [i for i in self.integrations.values() if i.status == status]
        return list(self.integrations.values())

    def disable_integration(self, integration_id: str) -> bool:
        return self.update_status(integration_id, IntegrationStatus.INACTIVE)

    def enable_integration(self, integration_id: str) -> bool:
        return self.update_status(integration_id, IntegrationStatus.ACTIVE)

    def count(self) -> int:
        return len(self.integrations)
