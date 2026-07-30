from __future__ import annotations

import logging
import os
from typing import Any

from .code_config import CodeConfig
from .code_models import CodeFile, CodeLanguage


_LANG_MAP: dict[str, CodeLanguage] = {
    ".py": CodeLanguage.PYTHON,
    ".js": CodeLanguage.JAVASCRIPT,
    ".ts": CodeLanguage.TYPESCRIPT,
    ".tsx": CodeLanguage.TYPESCRIPT,
    ".java": CodeLanguage.JAVA,
    ".cs": CodeLanguage.CSHARP,
    ".cpp": CodeLanguage.CPP,
    ".h": CodeLanguage.CPP,
    ".rs": CodeLanguage.RUST,
    ".go": CodeLanguage.GO,
    ".kt": CodeLanguage.KOTLIN,
    ".swift": CodeLanguage.SWIFT,
    ".php": CodeLanguage.PHP,
    ".rb": CodeLanguage.RUBY,
    ".dart": CodeLanguage.DART,
}


class CodeScanner:
    """Scans project directories for code files."""

    def __init__(self, config: CodeConfig | None = None) -> None:
        self.config = config or CodeConfig()
        self._log = logging.getLogger("superdev.code.scanner")

    def scan(self, path: str) -> list[CodeFile]:
        files: list[CodeFile] = []
        if not os.path.isdir(path):
            self._log.warning("Path not found: %s", path)
            return files
        for root, dirs, names in os.walk(path):
            if not self.config.include_hidden:
                dirs[:] = [d for d in dirs if not d.startswith(".")]
            depth = root.replace(path, "").count(os.sep)
            if depth > self.config.max_depth:
                continue
            for name in names:
                ext = os.path.splitext(name)[1].lower()
                if ext not in self.config.allowed_extensions:
                    continue
                full = os.path.join(root, name)
                try:
                    with open(full, "r", encoding="utf-8") as f:
                        content = f.read()
                except Exception:
                    continue
                lang = _LANG_MAP.get(ext, CodeLanguage.UNKNOWN)
                files.append(CodeFile(path=full, language=lang, content=content, size=len(content)))
        self._log.info("Scanned %d files in %s", len(files), path)
        return files
