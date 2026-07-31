"""Config engine."""
from __future__ import annotations

import time
from typing import Any


class ConfigEngine:
    def __init__(self) -> None:
        self._configs: dict[str, dict[str, Any]] = {}
        self._started = False
    def start(self) -> None:
        self._started = True
    def set(self, key: str, value: Any, namespace: str = "default") -> dict[str, Any]:
        config = {"key": key, "value": value, "namespace": namespace, "updated_at": time.time()}
        self._configs[f"{namespace}/{key}"] = config
        return config
    def get(self, key: str, namespace: str = "default") -> Any:
        return self._configs.get(f"{namespace}/{key}", {}).get("value")
    def delete(self, key: str, namespace: str = "default") -> bool:
        full_key = f"{namespace}/{key}"
        if full_key in self._configs:
            del self._configs[full_key]
            return True
        return False
    def list_namespace(self, namespace: str = "default") -> list[dict[str, Any]]:
        return [c for c in self._configs.values() if c.get("namespace") == namespace]
    def list_all(self) -> list[dict[str, Any]]:
        return list(self._configs.values())
    def count(self) -> int:
        return len(self._configs)
    def is_running(self) -> bool:
        return self._started
