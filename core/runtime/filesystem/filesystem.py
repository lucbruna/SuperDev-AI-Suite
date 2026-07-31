from __future__ import annotations

from pathlib import Path


class RuntimeFilesystem:
    def __init__(self, base_dir: str | Path | None = None) -> None:
        self._base_dir = Path(base_dir) if base_dir else Path.cwd() / ".runtime"

    async def create_temp_dir(self, session_id: str) -> Path:
        session_dir = self._base_dir / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        return session_dir

    def _resolve_path(self, session_id: str, path: str) -> Path:
        session_root = (self._base_dir / session_id).resolve()
        full_path = (session_root / path).resolve()
        if not full_path.is_relative_to(session_root):
            raise ValueError(
                f"path escapes the sandbox for session {session_id!r}: "
                f"{path!r}")
        return full_path

    async def write_file(self, session_id: str, path: str, content: str) -> Path:
        full_path = self._resolve_path(session_id, path)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")
        return full_path

    async def read_file(self, session_id: str, path: str) -> str:
        full_path = self._resolve_path(session_id, path)
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {full_path}")
        return full_path.read_text(encoding="utf-8")

    async def delete_file(self, session_id: str, path: str) -> bool:
        full_path = self._resolve_path(session_id, path)
        if not full_path.exists():
            return False
        full_path.unlink()
        return True

    async def list_files(self, session_id: str, directory: str = ".") -> list[dict[str, object]]:
        dir_path = self._resolve_path(session_id, directory)
        if not dir_path.exists() or not dir_path.is_dir():
            return []
        entries: list[dict[str, object]] = []
        for entry in dir_path.iterdir():
            entries.append({
                "name": entry.name,
                "path": str(entry),
                "is_dir": entry.is_dir(),
                "size": entry.stat().st_size if entry.is_file() else 0,
            })
        return entries

    async def session_dir(self, session_id: str) -> Path:
        return self._base_dir / session_id
