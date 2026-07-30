from __future__ import annotations

import os
import platform
from typing import Any


class ToolRuntime:
    """Provides runtime environment information to tools."""

    def __init__(self) -> None:
        self._variables: dict[str, str] = {}
        self._features: dict[str, bool] = {}

    def detect_platform(self) -> str:
        return platform.system().lower()

    def detect_architecture(self) -> str:
        return platform.machine()

    def get_python_version(self) -> str:
        return platform.python_version()

    def has_command(self, command: str) -> bool:
        path = os.environ.get("PATH", "")
        for directory in path.split(os.pathsep):
            full = os.path.join(directory, command)
            if os.path.isfile(full) or os.path.isfile(full + ".exe"):
                return True
        return False

    def set_variable(self, name: str, value: str) -> str:
        self._variables[name] = value
        return name

    def get_variable(self, name: str) -> str | None:
        return self._variables.get(name)

    def enable_feature(self, name: str) -> None:
        self._features[name] = True

    def disable_feature(self, name: str) -> None:
        self._features[name] = False

    def has_feature(self, name: str) -> bool:
        return self._features.get(name, False)

    def get_environment(self) -> dict[str, str]:
        return {
            "platform": self.detect_platform(),
            "architecture": self.detect_architecture(),
            "python": self.get_python_version(),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "platform": self.detect_platform(),
            "architecture": self.detect_architecture(),
            "python_version": self.get_python_version(),
            "variables": dict(self._variables),
            "features": dict(self._features),
        }
