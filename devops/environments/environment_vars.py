from __future__ import annotations

import logging
from typing import Any


class EnvironmentVars:
    """Stores and resolves environment variables across environments."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.devops.environments.vars")
        self._vars: dict[str, dict[str, Any]] = {}

    def set(self, environment: str, key: str, value: Any) -> None:
        raise NotImplementedError

    def get(self, environment: str, key: str) -> Any:
        raise NotImplementedError

    def resolve(self, environment: str) -> dict[str, Any]:
        raise NotImplementedError

    def import_from_file(self, environment: str, path: str) -> int:
        raise NotImplementedError

    def export_to_file(self, environment: str, path: str) -> int:
        raise NotImplementedError

    def secret_mask(self, environment: str, keys: list[str]) -> None:
        raise NotImplementedError
