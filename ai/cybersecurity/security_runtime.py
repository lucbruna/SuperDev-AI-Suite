"""
Security Runtime
"""

from enum import Enum
from typing import Any


class RuntimeState(Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    ERROR = "error"


class SecurityRuntime:
    def __init__(self):
        self.state = RuntimeState.STOPPED
        self.config: dict[str, Any] = {}
        self.services: dict[str, Any] = {}
        self.health_checks: dict[str, bool] = {}

    def start(self) -> None:
        self.state = RuntimeState.RUNNING

    def stop(self) -> None:
        self.state = RuntimeState.STOPPED

    def is_running(self) -> bool:
        return self.state == RuntimeState.RUNNING

    def register_service(self, name: str, service: Any) -> None:
        self.services[name] = service

    def get_service(self, name: str) -> Any | None:
        return self.services.get(name)

    def health_check(self, name: str) -> bool:
        return self.health_checks.get(name, True)

    def set_health(self, name: str, healthy: bool) -> None:
        self.health_checks[name] = healthy

    def get_overall_health(self) -> bool:
        if not self.health_checks:
            return True
        return all(self.health_checks.values())
