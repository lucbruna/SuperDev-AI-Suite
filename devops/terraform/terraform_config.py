from __future__ import annotations

import logging
from typing import Any


class TerraformConfig:
    """Builds Terraform configuration blocks programmatically."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.devops.terraform.config")
        self._blocks: list[dict[str, Any]] = []

    def provider(self, name: str, **kwargs: Any) -> "TerraformConfig":
        raise NotImplementedError

    def resource(self, type_: str, name: str, **kwargs: Any) -> "TerraformConfig":
        raise NotImplementedError

    def data(self, type_: str, name: str, **kwargs: Any) -> "TerraformConfig":
        raise NotImplementedError

    def variable(self, name: str, **kwargs: Any) -> "TerraformConfig":
        raise NotImplementedError

    def output(self, name: str, value: str) -> "TerraformConfig":
        raise NotImplementedError

    def module(self, name: str, source: str, **kwargs: Any) -> "TerraformConfig":
        raise NotImplementedError

    def render(self) -> str:
        raise NotImplementedError
