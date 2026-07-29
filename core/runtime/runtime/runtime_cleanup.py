from __future__ import annotations

import asyncio
import logging
import shutil
import time
from pathlib import Path

logger = logging.getLogger(__name__)


class RuntimeCleanup:
    def __init__(self, session_base_dir: str | Path | None = None) -> None:
        self._base_dir = Path(session_base_dir) if session_base_dir else Path.cwd() / ".runtime"
        self._cleanup_tasks: dict[str, asyncio.Task] = {}

    async def cleanup_session(self, session_id: str) -> None:
        session_dir = self._base_dir / session_id
        if session_dir.exists():
            shutil.rmtree(session_dir, ignore_errors=True)
            logger.info("Cleaned up session directory: %s", session_dir)

    async def cleanup_all(self) -> None:
        if self._base_dir.exists():
            for item in self._base_dir.iterdir():
                if item.is_dir():
                    shutil.rmtree(item, ignore_errors=True)
            logger.info("Cleaned up all session directories")

    async def cleanup_expired(self, max_age: int = 3600) -> int:
        now = time.time()
        count = 0
        if not self._base_dir.exists():
            return 0
        for item in self._base_dir.iterdir():
            if item.is_dir():
                mtime = item.stat().st_mtime
                if now - mtime > max_age:
                    shutil.rmtree(item, ignore_errors=True)
                    count += 1
        logger.info("Cleaned up %d expired session directories", count)
        return count
