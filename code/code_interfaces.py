from __future__ import annotations

from typing import Any, Protocol

from .code_models import CodeFile, CodeIssue, CodeModule


class CodeScannerInterface(Protocol):
    def scan(self, path: str) -> list[CodeFile]: ...


class CodeAnalyzerInterface(Protocol):
    def analyze(self, files: list[CodeFile]) -> list[CodeIssue]: ...


class CodeGeneratorInterface(Protocol):
    def generate(self, specification: dict[str, Any]) -> list[CodeFile]: ...


class CodeRepositoryInterface(Protocol):
    def save(self, module: CodeModule) -> None: ...
    def get(self, module_id: str) -> CodeModule | None: ...
