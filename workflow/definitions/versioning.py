from __future__ import annotations

from typing import Any


class VersionManager:
    """Manages workflow version numbers."""

    @staticmethod
    def bump_major(version: str) -> str:
        parts = version.split(".")
        return f"{int(parts[0]) + 1}.0.0"

    @staticmethod
    def bump_minor(version: str) -> str:
        parts = version.split(".")
        return f"{parts[0]}.{int(parts[1]) + 1}.0"

    @staticmethod
    def bump_patch(version: str) -> str:
        parts = version.split(".")
        return f"{parts[0]}.{parts[1]}.{int(parts[2]) + 1}"

    @staticmethod
    def compare(v1: str, v2: str) -> int:
        p1 = [int(x) for x in v1.split(".")]
        p2 = [int(x) for x in v2.split(".")]
        for a, b in zip(p1, p2):
            if a < b:
                return -1
            if a > b:
                return 1
        return 0
