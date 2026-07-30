from __future__ import annotations

import logging
from typing import Any


class TestReport:
    """Generates test execution reports."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.testing.report")

    def generate(self, results: dict[str, Any], format: str = "json") -> str:
        self._log.info("Generating %s report", format)
        return ""

    def summary(self, results: dict[str, Any]) -> str:
        passed = results.get("passed", 0)
        failed = results.get("failed", 0)
        total = passed + failed
        return f"{passed}/{total} passed ({failed} failed)"
