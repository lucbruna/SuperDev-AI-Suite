from __future__ import annotations

import logging
from typing import Any

from .code_models import CodeFile, CodeIssue
from .code_scanner import CodeScanner


class CodeManager:
    """Coordinates code scanning, analysis, and generation."""

    def __init__(self) -> None:
        self.scanner = CodeScanner()
        self._log = logging.getLogger("superdev.code.manager")

    def scan(self, path: str) -> list[CodeFile]:
        return self.scanner.scan(path)

    def analyze(self, files: list[CodeFile]) -> list[CodeIssue]:
        return []

    def generate(self, spec: dict[str, Any]) -> list[CodeFile]:
        return []
