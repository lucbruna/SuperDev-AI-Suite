from __future__ import annotations

import asyncio
import os
import shutil
import sys

from runtime_engine.runtime.runtime import BaseRuntime, ExecutionResult
from runtime_engine.core.configuration import RuntimeConfig


class ShellRuntime(BaseRuntime):
    def __init__(self, config: RuntimeConfig | None = None, shell_type: str | None = None) -> None:
        super().__init__(config)
        self._shell = shell_type or self._detect_shell()

    def _detect_shell(self) -> str:
        if sys.platform == "win32":
            return "powershell.exe"
        for shell in ["bash", "zsh", "sh"]:
            if shutil.which(shell):
                return shell
        return "sh"

    async def execute(self, command: str, language: str = "shell", config: RuntimeConfig | None = None) -> ExecutionResult:
        cfg = config or self.config
        shell_cmd = self._shell
        if sys.platform == "win32":
            return await self._run_subprocess(
                [shell_cmd, "-Command", command],
                timeout=cfg.default_timeout,
            )
        return await self._run_subprocess(
            [shell_cmd, "-c", command],
            timeout=cfg.default_timeout,
        )

    async def execute_script(self, script_path: str, config: RuntimeConfig | None = None) -> ExecutionResult:
        cfg = config or self.config
        return await self._run_subprocess(
            [self._shell, script_path],
            timeout=cfg.default_timeout,
        )
