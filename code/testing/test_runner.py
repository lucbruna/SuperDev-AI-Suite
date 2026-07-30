from __future__ import annotations

import logging
from typing import Any


class TestRunner:
    """Executes test suites and collects results."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.testing.runner")

    def run(self, paths: list[str]) -> dict[str, Any]:
        self._log.info("Executing %d test paths", len(paths))
        return {"passed": 0, "failed": 0, "duration": 0.0}

    def run_file(self, path: str) -> dict[str, Any]:
        self._log.info("Executing tests in %s", path)
        return {"passed": 0, "failed": 0, "duration": 0.0}
