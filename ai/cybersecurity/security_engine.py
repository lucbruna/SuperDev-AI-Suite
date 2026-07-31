"""
Security Engine - Main orchestrator
"""

from typing import Any


class SecurityEngine:
    def __init__(self):
        self.running = False
        self.modules: dict[str, Any] = {}
        self.config: dict[str, Any] = {}
        self.metrics: dict[str, int] = {}

    def start(self) -> None:
        self.running = True

    def stop(self) -> None:
        self.running = False

    def is_running(self) -> bool:
        return self.running

    def register_module(self, name: str, module: Any) -> None:
        self.modules[name] = module

    def get_module(self, name: str) -> Any | None:
        return self.modules.get(name)

    def list_modules(self) -> list:
        return list(self.modules.keys())

    def set_config(self, key: str, value: Any) -> None:
        self.config[key] = value

    def get_config(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)

    def increment_metric(self, name: str) -> None:
        self.metrics[name] = self.metrics.get(name, 0) + 1

    def get_metric(self, name: str) -> int:
        return self.metrics.get(name, 0)

    def get_metrics(self) -> dict[str, int]:
        return self.metrics.copy()

    def health_check(self) -> bool:
        return self.running and all(
            hasattr(m, "is_healthy") and m.is_healthy() if hasattr(m, "is_healthy") else True
            for m in self.modules.values()
        )
