"""Storage Monitor — reports downloads-directory usage."""
from __future__ import annotations

from typing import Any


class StorageMonitor:
    """Sums file sizes under the studio downloads directory."""

    def collect(self) -> dict[str, Any]:
        from modules.ai_video_studio.media.output_paths import get_downloads_dir

        root = get_downloads_dir()
        total = 0
        files = 0
        for path in root.rglob("*"):
            if path.is_file():
                try:
                    total += path.stat().st_size
                    files += 1
                except OSError:
                    continue
        return {
            "root": str(root),
            "files": files,
            "bytes": total,
            "mb": round(total / (1024 * 1024), 2),
        }


_storage_monitor: StorageMonitor | None = None


def get_storage_monitor() -> StorageMonitor:
    global _storage_monitor
    if _storage_monitor is None:
        _storage_monitor = StorageMonitor()
    return _storage_monitor
