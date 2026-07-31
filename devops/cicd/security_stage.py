from __future__ import annotations

import logging
from typing import Any


class SecurityStage:
    """CI/CD security stage — SAST, DAST, dependency scanning."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.devops.cicd.security")

    def run(self, config: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    def validate(self, config: dict[str, Any]) -> list[str]:
        raise NotImplementedError
