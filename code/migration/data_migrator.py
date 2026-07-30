from __future__ import annotations

import logging
from typing import Any


class DataMigrator:
    """Handles data-level migrations."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.migration.data")

    def transform(self, data: dict[str, Any], rules: list[dict[str, Any]]) -> dict[str, Any]:
        self._log.info("Transforming data with %d rules", len(rules))
        return data

    def validate(self, data: dict[str, Any], schema: dict[str, Any]) -> list[str]:
        errors: list[str] = []
        for key in schema:
            if key not in data:
                errors.append(f"Missing key: {key}")
        return errors
