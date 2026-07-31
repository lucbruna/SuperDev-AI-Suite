from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .cloud_engine import CloudEngine


class CloudMigration:
    """Migrates workloads between providers, regions, or accounts."""

    def __init__(self, engine: CloudEngine) -> None:
        self._log = logging.getLogger("superdev.devops.cloud.migration")
        self._engine = engine

    def plan(self, source: str, target: str, resources: list[str]) -> dict[str, Any]:
        raise NotImplementedError

    def execute(self, migration_id: str) -> dict[str, Any]:
        raise NotImplementedError

    def rollback(self, migration_id: str) -> bool:
        raise NotImplementedError

    def status(self, migration_id: str) -> dict[str, Any]:
        raise NotImplementedError
