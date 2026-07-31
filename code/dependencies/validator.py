from __future__ import annotations

import logging
from typing import Any


class DependencyValidator:
    """Validates dependency configurations."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.dependencies.validator")

    def validate(self, config: dict[str, Any]) -> list[str]:
        errors: list[str] = []
        deps = config.get("dependencies", {})
        for name, version in deps.items():
            if not isinstance(version, str):
                errors.append(f"{name}: version must be a string")
        return errors
