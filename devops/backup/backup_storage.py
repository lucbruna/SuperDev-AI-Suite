from __future__ import annotations

import logging
from typing import Any


class BackupStorage:
    """Manages backup storage backends and lifecycle."""

    def __init__(self, backend: str = "local") -> None:
        self._log = logging.getLogger("superdev.devops.backup.storage")
        self.backend = backend

    def store(self, backup_id: str, data: Any, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError

    def retrieve(self, backup_id: str) -> Any:
        raise NotImplementedError

    def delete(self, backup_id: str) -> bool:
        raise NotImplementedError

    def list(self, prefix: str | None = None) -> list[dict[str, Any]]:
        raise NotImplementedError

    def apply_retention(self, policy: dict[str, Any]) -> list[str]:
        raise NotImplementedError
