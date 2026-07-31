from __future__ import annotations

import logging
from typing import Any


class TerraformModule:
    """Loads and manages Terraform modules."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.devops.terraform.module")

    def registry_info(self, source: str) -> dict[str, Any]:
        raise NotImplementedError

    def init(self, source: str, version: str | None = None, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError

    def update(self, module: str) -> dict[str, Any]:
        raise NotImplementedError

    def list_local(self, directory: str) -> list[dict[str, Any]]:
        raise NotImplementedError
