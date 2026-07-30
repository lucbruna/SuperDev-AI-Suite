from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CodeConfig:
    max_file_size: int = 1_000_000
    allowed_extensions: list[str] = field(default_factory=lambda: [".py", ".js", ".ts", ".tsx", ".java", ".cs", ".cpp", ".h", ".rs", ".go", ".kt", ".swift", ".php", ".rb", ".dart"])
    max_depth: int = 10
    include_hidden: bool = False
    timeout_seconds: int = 120
