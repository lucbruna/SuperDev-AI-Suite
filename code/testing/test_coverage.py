from __future__ import annotations

import logging
from typing import Any


class TestCoverage:
    """Measures code coverage from test runs."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.testing.coverage")
        self._data: dict[str, Any] = {}

    def start(self) -> None:
        self._log.info("Coveration collection started")

    def stop(self) -> dict[str, Any]:
        return {"lines_total": 0, "lines_covered": 0, "coverage": 0.0, "files": {}}

    def report(self) -> str:
        return "Coveration: 0.0%"
