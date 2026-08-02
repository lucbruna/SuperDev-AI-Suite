"""Python runtime — facade over venv/pip/poetry/uv/pytest (Volume 12, Fase 17)."""
from __future__ import annotations

import sys
from typing import Any

from modules.aios.kernel.kernel_logger import get_kernel_logger
from modules.aios.python.pip_manager import PipManager
from modules.aios.python.poetry_manager import PoetryManager, PoetryUnavailableError
from modules.aios.python.pytest_runner import PytestRunner
from modules.aios.python.requirements import (
    parse_requirements,
    render_requirements,
)
from modules.aios.python.uv_manager import UvManager, UvUnavailableError
from modules.aios.python.venv_manager import VenvManager


class PythonRuntime:
    """Facade over the Python toolchain.

    Stateless: managers are CLI wrappers. ``close`` is a no-op. Tools that are
    not installed (poetry) degrade gracefully via their *UnavailableError.
    """

    def __init__(self, python: str | None = None) -> None:
        self.python = python or sys.executable
        self.venvs = VenvManager(python=self.python)
        self.pip = PipManager(python=self.python)
        self.poetry = PoetryManager()
        self.uv = UvManager()
        self.pytest = PytestRunner(python=self.python)
        self._logger = get_kernel_logger()

    def parse_requirements(self, text: str) -> list[Any]:
        return parse_requirements(text)

    def render_requirements(self, requirements: list[Any]) -> str:
        return render_requirements(requirements)

    async def snapshot(self) -> dict[str, Any]:
        """Best-effort tool inventory; each tool degrades to None on error."""
        python_version = self.python
        try:
            import platform

            python_version = platform.python_version()
        except Exception:  # noqa: BLE001
            python_version = sys.version.split()[0]
        uv_version: str | None = None
        poetry_version: str | None = None
        try:
            uv_version = (await self.uv.version())["version"]
        except (UvUnavailableError, RuntimeError):
            uv_version = None
        try:
            poetry_version = (await self.poetry.version())["version"]
        except (PoetryUnavailableError, RuntimeError):
            poetry_version = None
        return {
            "python": python_version,
            "uv": uv_version,
            "poetry": poetry_version,
            "venv": {"python": self.venvs.python},
        }

    async def close(self) -> None:
        """No-op — the python runtime is stateless. Venvs are not removed."""


_python_runtime: PythonRuntime | None = None


def get_python_runtime() -> PythonRuntime:
    global _python_runtime
    if _python_runtime is None:
        _python_runtime = PythonRuntime()
    return _python_runtime


__all__ = ["PythonRuntime", "get_python_runtime"]
