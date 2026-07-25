from __future__ import annotations

import asyncio
import sys
import tempfile
from pathlib import Path

from runtime_engine.runtime.runtime import BaseRuntime, ExecutionResult
from runtime_engine.core.configuration import RuntimeConfig


class PythonRuntime(BaseRuntime):
    def __init__(self, config: RuntimeConfig | None = None) -> None:
        super().__init__(config)
        self._venv_path: Path | None = None

    async def check_version(self) -> str:
        result = await self._run_subprocess([sys.executable, "--version"])
        return result.stdout.strip()

    async def create_venv(self, path: str | Path | None = None) -> Path:
        self._venv_path = Path(path) if path else Path(tempfile.mkdtemp(prefix="pyvenv_"))
        result = await self._run_subprocess([sys.executable, "-m", "venv", str(self._venv_path)])
        if result.exit_code != 0:
            raise RuntimeError(f"Failed to create venv: {result.stderr}")
        return self._venv_path

    async def pip_install(self, packages: list[str]) -> ExecutionResult:
        pip = str(self._venv_path / "bin" / "pip") if self._venv_path else "pip"
        return await self._run_subprocess([pip, "install", *packages])

    async def execute(self, code: str, language: str = "python", config: RuntimeConfig | None = None) -> ExecutionResult:
        cfg = config or self.config
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(code)
            f.flush()
            filepath = f.name
        try:
            return await self.execute_file(filepath, cfg)
        finally:
            Path(filepath).unlink(missing_ok=True)

    async def execute_file(self, filepath: str, config: RuntimeConfig | None = None) -> ExecutionResult:
        cfg = config or self.config
        python = str(self._venv_path / "bin" / "python") if self._venv_path else sys.executable
        return await self._run_subprocess(
            [python, filepath],
            timeout=cfg.default_timeout,
        )
