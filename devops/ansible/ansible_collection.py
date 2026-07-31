from __future__ import annotations

import logging
from typing import Any


class AnsibleCollection:
    """Manages Ansible Galaxy collections."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.devops.ansible.collection")

    def search(self, query: str) -> list[dict[str, Any]]:
        raise NotImplementedError

    def install(self, collection: str, version: str | None = None, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError

    def upgrade(self, collection: str) -> dict[str, Any]:
        raise NotImplementedError

    def uninstall(self, collection: str) -> bool:
        raise NotImplementedError

    def list_installed(self) -> list[dict[str, Any]]:
        raise NotImplementedError
