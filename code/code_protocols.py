from __future__ import annotations

from typing import Any, Protocol

from .code_models import CodeFile, CodeIssue


class CodeLifecycle(Protocol):
    async def on_scan(self, files: list[CodeFile]) -> None: ...
    async def on_analyze(self, issues: list[CodeIssue]) -> None: ...
    async def on_generate(self, files: list[CodeFile]) -> None: ...


class CodeValidator(Protocol):
    def validate(self, file: CodeFile) -> list[CodeIssue]: ...
