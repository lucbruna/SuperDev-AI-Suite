from __future__ import annotations

import fnmatch
import os
from pathlib import Path
from typing import Any


class FileSystemPolicy:
    def __init__(
        self,
        allowed_paths: list[str] | None = None,
        blocked_patterns: list[str] | None = None,
        read_only: bool = False,
    ) -> None:
        self.allowed_paths = [os.path.abspath(p) for p in (allowed_paths or ["."])]
        self.blocked_patterns = blocked_patterns or ["*.secret", "*.key", "*.pem", ".env*", "__pycache__/*"]
        self.read_only = read_only

    def check(self, path: str, operation: str = "read") -> None:
        abs_path = os.path.abspath(path)

        if operation in ("write", "delete", "modify") and self.read_only:
            raise PermissionError(f"Filesystem is read-only: cannot {operation} '{path}'")

        if not self._is_in_allowed_paths(abs_path):
            raise PermissionError(f"Path '{path}' is not in allowed directories: {self.allowed_paths}")

        for pattern in self.blocked_patterns:
            if fnmatch.fnmatch(abs_path, pattern) or fnmatch.fnmatch(os.path.basename(abs_path), pattern):
                raise PermissionError(f"Path '{path}' matches blocked pattern '{pattern}'")

        for pattern in self.blocked_patterns:
            path_parts = abs_path.replace("\\", "/").split("/")
            pattern_parts = pattern.replace("\\", "/").split("/")
            if len(pattern_parts) <= len(path_parts):
                subpath = "/".join(path_parts[-len(pattern_parts):])
                if fnmatch.fnmatch(subpath, pattern):
                    raise PermissionError(f"Path '{path}' matches blocked pattern '{pattern}'")

    def _is_in_allowed_paths(self, abs_path: str) -> bool:
        for allowed in self.allowed_paths:
            allowed_abs = os.path.abspath(allowed)
            if abs_path == allowed_abs or abs_path.startswith(allowed_abs + os.sep):
                return True
        return False

    def add_allowed_path(self, path: str) -> None:
        self.allowed_paths.append(os.path.abspath(path))

    def add_blocked_pattern(self, pattern: str) -> None:
        self.blocked_patterns.append(pattern)