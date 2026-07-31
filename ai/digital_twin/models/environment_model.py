"""Environment model."""

from __future__ import annotations

import time
import uuid
from typing import Any


class EnvironmentModel:
    def __init__(self) -> None:
        self._environments: dict[str, dict[str, Any]] = {}

    def create(self, name: str, parameters: dict[str, Any] = None) -> dict[str, Any]:
        env_id = str(uuid.uuid4())[:8]
        env = {
            "env_id": env_id,
            "name": name,
            "parameters": parameters or {},
            "conditions": {},
            "created_at": time.time(),
        }
        self._environments[env_id] = env
        return env

    def get(self, env_id: str) -> dict[str, Any]:
        return self._environments.get(env_id, {"error": "not_found"})

    def set_condition(self, env_id: str, key: str, value: Any) -> bool:
        if env_id not in self._environments:
            return False
        self._environments[env_id]["conditions"][key] = value
        return True

    def get_conditions(self, env_id: str) -> dict[str, Any]:
        return self._environments.get(env_id, {}).get("conditions", {})

    def update_parameters(self, env_id: str, params: dict[str, Any]) -> bool:
        if env_id not in self._environments:
            return False
        self._environments[env_id]["parameters"].update(params)
        return True

    def list_all(self) -> list[dict[str, Any]]:
        return list(self._environments.values())

    def count(self) -> int:
        return len(self._environments)
