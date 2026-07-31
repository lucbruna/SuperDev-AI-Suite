from __future__ import annotations

import copy
import logging
from typing import Any


class WebConfiguration:
    """Web-specific configuration and environment settings."""

    REQUIRED_KEYS = ("app_name", "base_url")

    def __init__(self, **kwargs: Any) -> None:
        self._log = logging.getLogger("superdev.frontend.web.config")
        self._config: dict[str, Any] = dict(kwargs)

    def load(self, source: dict[str, Any] | None = None) -> dict[str, Any]:
        if source:
            self._config.update(copy.deepcopy(source))
        return copy.deepcopy(self._config)

    def get(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._config[key] = value

    def validate(self) -> list[str]:
        errors = []
        for key in self.REQUIRED_KEYS:
            if not self._config.get(key):
                errors.append(f"missing required key: {key}")
        return errors

    def export(self) -> dict[str, Any]:
        return copy.deepcopy(self._config)
