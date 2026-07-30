from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class CodeLanguage(Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CSHARP = "csharp"
    CPP = "cpp"
    RUST = "rust"
    GO = "go"
    KOTLIN = "kotlin"
    SWIFT = "swift"
    PHP = "php"
    RUBY = "ruby"
    DART = "dart"
    UNKNOWN = "unknown"


class CodeIssueSeverity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    HINT = "hint"


@dataclass
class CodeFile:
    path: str
    language: CodeLanguage = CodeLanguage.UNKNOWN
    content: str = ""
    size: int = 0


@dataclass
class CodeIssue:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    file: str = ""
    line: int = 0
    column: int = 0
    severity: CodeIssueSeverity = CodeIssueSeverity.WARNING
    message: str = ""
    rule: str = ""


@dataclass
class CodeModule:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    path: str = ""
    language: CodeLanguage = CodeLanguage.UNKNOWN
    files: list[CodeFile] = field(default_factory=list)
