from __future__ import annotations

import logging
from typing import Any


class BuildStage:
    """CI/CD build stage — compiles, packages, or transpiles code."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.devops.cicd.build")

    def run(self, config: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    def validate(self, config: dict[str, Any]) -> list[str]:
        raise NotImplementedError
