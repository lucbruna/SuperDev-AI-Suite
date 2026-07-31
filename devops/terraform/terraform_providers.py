from __future__ import annotations

import logging
from typing import Any


class TerraformProviderRegistry:
    """Registers and resolves Terraform providers and versions."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.devops.terraform.providers")
        self._providers: dict[str, dict[str, Any]] = {}

    def register(self, name: str, version: str, **kwargs: Any) -> None:
        raise NotImplementedError

    def resolve(self, name: str, constraint: str | None = None) -> dict[str, Any]:
        raise NotImplementedError

    def available(self) -> list[dict[str, Any]]:
        raise NotImplementedError

    def lock(self, directory: str) -> dict[str, Any]:
        raise NotImplementedError
