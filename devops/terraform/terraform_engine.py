from __future__ import annotations

import logging
from typing import Any

from ..devops_context import DevOpsContext


class TerraformEngine:
    """Manages Terraform infrastructure-as-code workflows."""

    def __init__(self, context: DevOpsContext | None = None) -> None:
        self._log = logging.getLogger("superdev.devops.terraform")
        self._context = context

    def init(self, directory: str, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError

    def plan(self, directory: str, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError

    def apply(self, directory: str, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError

    def destroy(self, directory: str, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError

    def validate(self, directory: str) -> dict[str, Any]:
        raise NotImplementedError

    def fmt(self, directory: str) -> dict[str, Any]:
        raise NotImplementedError

    def state_list(self, directory: str) -> list[str]:
        raise NotImplementedError

    def state_show(self, directory: str, resource: str) -> dict[str, Any]:
        raise NotImplementedError

    def state_rm(self, directory: str, resource: str) -> bool:
        raise NotImplementedError

    def output(self, directory: str, name: str | None = None) -> dict[str, Any]:
        raise NotImplementedError
