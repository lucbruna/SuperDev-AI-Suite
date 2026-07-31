from __future__ import annotations

import logging
from typing import Any


class VersionMigrator:
    """Handles version-to-version migrations."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.migration.version")

    def migrate_version(self, code: str, from_version: str, to_version: str) -> str:
        self._log.info("Migrating code from %s to %s", from_version, to_version)
        return code
