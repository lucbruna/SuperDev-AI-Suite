from __future__ import annotations

import logging
from typing import Any


class TerraformWorkspace:
    """Manages Terraform workspaces for environment isolation."""

    def __init__(self, directory: str) -> None:
        self._log = logging.getLogger("superdev.devops.terraform.workspace")
        self._directory = directory

    def list(self) -> list[str]:
        raise NotImplementedError

    def select(self, name: str) -> bool:
        raise NotImplementedError

    def create(self, name: str) -> bool:
        raise NotImplementedError

    def delete(self, name: str) -> bool:
        raise NotImplementedError

    def current(self) -> str:
        raise NotImplementedError
