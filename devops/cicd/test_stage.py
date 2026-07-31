from __future__ import annotations

import logging
from typing import Any


class TestStage:
    """CI/CD test stage — runs unit, integration, and e2e tests."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.devops.cicd.test")

    def run(self, config: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    def validate(self, config: dict[str, Any]) -> list[str]:
        raise NotImplementedError
