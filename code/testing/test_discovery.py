from __future__ import annotations

import logging
from pathlib import Path


class TestDiscovery:
    """Discovers test files in the project."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.testing.discovery")

    def discover(self, root: str, pattern: str = "*_test.py") -> list[Path]:
        self._log.info("Discovering tests in %s", root)
        return list(Path(root).rglob(pattern))

    def by_type(self, root: str) -> dict[str, list[Path]]:
        return {
            "unit": list(Path(root).rglob("*_test.py")),
            "integration": list(Path(root).rglob("*_integration.py")),
            "e2e": list(Path(root).rglob("*_e2e.py")),
        }
