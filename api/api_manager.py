from __future__ import annotations

from typing import Any

from .api_config import APIConfigManager
from .api_events import APIEventBus, APIEventType
from .api_factory import APIFactory
from .api_health import APIHealth
from .api_logger import APILogger
from .api_metrics import APIMetrics
from .api_permissions import APIPermissions
from .api_registry import APIRegistry
from .api_repository import APIRepository
from .api_router import APIRouter
from .api_runtime import APIRuntime
from .api_security import APISecurity
from .api_version import APIVersion


class APIManager:
    """Top-level manager for the entire API Engine."""

    def __init__(self) -> None:
        self.logger = APILogger()
        self.metrics = APIMetrics()
        self.events = APIEventBus()
        self.health = APIHealth()
        self.version = APIVersion()
        self.config = APIConfigManager()
        self.security = APISecurity()
        self.permissions = APIPermissions()
        self.registry = APIRegistry()
        self.repository = APIRepository(self.registry)
        self.router = APIRouter(self.registry)
        self.factory = APIFactory(self.registry)
        self.runtime = APIRuntime(self.registry, self.logger, self.metrics, self.events)
        self._initialized = False

    @property
    def is_healthy(self) -> bool:
        return True

    @property
    def route_registry(self) -> APIRouter:
        return self.router

    def initialize(self) -> None:
        self._initialized = True

    def get_status(self) -> dict[str, Any]:
        return self.to_dict()

    def to_dict(self) -> dict[str, Any]:
        return {
            "config": self.config.to_dict(),
            "version": self.version.to_dict(),
            "health": self.health.to_dict(),
            "metrics": self.metrics.to_dict(),
            "registry": self.registry.to_dict(),
            "router": self.router.to_dict(),
        }
