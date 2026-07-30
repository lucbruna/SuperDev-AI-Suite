from __future__ import annotations

import logging
from typing import Any

from .code_config import CodeConfig
from .code_manager import CodeManager
from .code_models import CodeFile, CodeIssue
from .code_registry import CodeRegistry


class CodeEngine:
    """Central orchestrator for code analysis and generation."""

    def __init__(self, config: CodeConfig | None = None) -> None:
        self.config = config or CodeConfig()
        self.manager = CodeManager()
        self.registry = CodeRegistry()
        self._log = logging.getLogger("superdev.code.engine")

    async def scan_project(self, path: str) -> list[CodeFile]:
        return self.manager.scan(path)

    async def analyze(self, files: list[CodeFile]) -> list[CodeIssue]:
        return self.manager.analyze(files)

    async def generate(self, spec: dict[str, Any]) -> list[CodeFile]:
        return self.manager.generate(spec)
