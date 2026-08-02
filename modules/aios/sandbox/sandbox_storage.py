"""Sandbox storage — isolated scratch directory per sandbox."""
from __future__ import annotations
import shutil
import tempfile
from pathlib import Path
from typing import Any, Callable

from modules.aios.kernel.kernel_logger import get_kernel_logger


class SandboxStorage:
    """Owns a private temp directory created for one sandbox.

    The directory is created lazily (first write) and removed on ``close``.
    All paths are confined under ``self.root``; callers must go through the
    ``write``/``read`` helpers so nothing escapes the sandbox.
    """

    def __init__(
        self,
        sandbox_id: str,
        base_dir: str | None = None,
        on_write: Callable[[int], None] | None = None,
    ) -> None:
        self.sandbox_id = sandbox_id
        self._base_dir = base_dir
        self._on_write = on_write
        self._root: Path | None = None
        self._logger = get_kernel_logger()
        self._created = False

    @property
    def root(self) -> Path:
        if self._root is None:
            self._root = Path(
                tempfile.mkdtemp(prefix=f"aios-{self.sandbox_id[:8]}-", dir=self._base_dir)
            )
            self._created = True
            self._logger.log("sandbox", f"storage created at {self._root}")
        return self._root

    @property
    def created(self) -> bool:
        return self._created

    def _confine(self, rel: str) -> Path:
        path = (self.root / rel).resolve()
        if not path.is_relative_to(self.root):
            raise ValueError(f"path escapes sandbox storage: {rel}")
        return path

    def write(self, rel: str, data: bytes | str) -> Path:
        """Write within the sandbox (creates the root on first use)."""
        path = self._confine(rel)
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(data, str):
            path.write_text(data, encoding="utf-8")
            size = len(data.encode("utf-8"))
        else:
            path.write_bytes(data)
            size = len(data)
        if self._on_write is not None:
            self._on_write(size)
        return path

    def read(self, rel: str) -> str:
        return self._confine(rel).read_text(encoding="utf-8")

    def exists(self, rel: str) -> bool:
        return self._confine(rel).exists()

    def list(self) -> list[str]:
        if not self._created:
            return []
        return [str(p.relative_to(self.root)) for p in sorted(self.root.rglob("*"))]

    def size_bytes(self) -> int:
        if not self._created:
            return 0
        return sum(p.stat().st_size for p in self.root.rglob("*") if p.is_file())

    def close(self) -> None:
        if self._root is not None:
            shutil.rmtree(self._root, ignore_errors=True)
            self._logger.log("sandbox", f"storage removed for {self.sandbox_id}")
            self._root = None
            self._created = False

    def snapshot(self) -> dict[str, Any]:
        return {
            "created": self._created,
            "root": str(self._root) if self._root else None,
            "files": self.list(),
            "size_bytes": self.size_bytes(),
        }


__all__ = ["SandboxStorage"]
