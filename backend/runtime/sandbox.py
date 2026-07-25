from __future__ import annotations

import asyncio
import os
import tempfile
import shutil
from pathlib import Path
from typing import Any

from backend.runtime.base_runtime import ResourceLimits


class SandboxManager:
    """Manages isolated execution environments for code runs."""

    def __init__(self, base_dir: str = "/tmp/superdev_sandbox"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def create_sandbox(self, run_id: str, limits: ResourceLimits | None = None) -> Path:
        sandbox_dir = self.base_dir / run_id
        sandbox_dir.mkdir(parents=True, exist_ok=True)

        (sandbox_dir / "src").mkdir(exist_ok=True)
        (sandbox_dir / "output").mkdir(exist_ok=True)
        (sandbox_dir / "tmp").mkdir(exist_ok=True)

        return sandbox_dir

    def cleanup_sandbox(self, run_id: str) -> bool:
        sandbox_dir = self.base_dir / run_id
        if sandbox_dir.exists():
            shutil.rmtree(sandbox_dir)
            return True
        return False

    def get_sandbox_path(self, run_id: str) -> Path | None:
        sandbox_dir = self.base_dir / run_id
        return sandbox_dir if sandbox_dir.exists() else None

    def list_sandboxes(self) -> list[str]:
        return [
            d.name for d in self.base_dir.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        ]

    def get_sandbox_size(self, run_id: str) -> int:
        sandbox_dir = self.base_dir / run_id
        if not sandbox_dir.exists():
            return 0
        total = 0
        for file in sandbox_dir.rglob("*"):
            if file.is_file():
                total += file.stat().st_size
        return total

    async def write_file(self, run_id: str, relative_path: str, content: str | bytes) -> Path:
        sandbox_dir = self.base_dir / run_id
        file_path = sandbox_dir / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)

        mode = "wb" if isinstance(content, bytes) else "w"
        with open(file_path, mode) as f:
            f.write(content)

        return file_path

    async def read_file(self, run_id: str, relative_path: str) -> bytes:
        sandbox_dir = self.base_dir / run_id
        file_path = sandbox_dir / relative_path
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {relative_path}")
        return file_path.read_bytes()

    def list_files(self, run_id: str, relative_path: str = ".") -> list[dict[str, Any]]:
        sandbox_dir = self.base_dir / run_id / relative_path
        if not sandbox_dir.exists():
            return []

        files = []
        for item in sorted(sandbox_dir.iterdir()):
            stat = item.stat()
            files.append({
                "name": item.name,
                "path": str(item.relative_to(self.base_dir / run_id)),
                "is_dir": item.is_dir(),
                "size": stat.st_size if item.is_file() else 0,
            })
        return files


sandbox_manager = SandboxManager()
