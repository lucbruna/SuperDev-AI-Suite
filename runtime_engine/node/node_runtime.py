from __future__ import annotations

import asyncio
import shutil
import tempfile
from pathlib import Path

from runtime_engine.runtime.runtime import BaseRuntime, ExecutionResult
from runtime_engine.core.configuration import RuntimeConfig


class NodeRuntime(BaseRuntime):
    def __init__(self, config: RuntimeConfig | None = None) -> None:
        super().__init__(config)
        self._node_path: str | None = shutil.which("node")

    async def check_version(self) -> str:
        if not self._node_path:
            return "Node.js not found"
        result = await self._run_subprocess([self._node_path, "--version"])
        return result.stdout.strip()

    async def execute(self, code: str, language: str = "node", config: RuntimeConfig | None = None) -> ExecutionResult:
        cfg = config or self.config
        return await self._run_subprocess(
            [self._node_path or "node", "-e", code],
            timeout=cfg.default_timeout,
        )

    async def execute_file(self, filepath: str, config: RuntimeConfig | None = None) -> ExecutionResult:
        cfg = config or self.config
        return await self._run_subprocess(
            [self._node_path or "node", filepath],
            timeout=cfg.default_timeout,
        )

    async def npm_install(self, packages: list[str], cwd: str | None = None) -> ExecutionResult:
        cmd = ["npm", "install", *packages] if packages else ["npm", "install"]
        return await self._run_subprocess(cmd, cwd=cwd)
