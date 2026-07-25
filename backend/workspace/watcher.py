import asyncio
from collections.abc import Callable
from pathlib import Path


class FileWatcher:
    def __init__(self, poll_interval: float = 1.0) -> None:
        self._poll_interval = poll_interval
        self._callbacks: list[Callable] = []
        self._running = False
        self._task: asyncio.Task | None = None
        self._mtimes: dict[str, float] = {}

    async def watch(self, path: str) -> None:
        self._running = True
        self._task = asyncio.create_task(self._poll_loop(path))

    def on_change(self, callback: Callable) -> None:
        self._callbacks.append(callback)

    async def stop(self) -> None:
        self._running = False
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def _poll_loop(self, path: str) -> None:
        base = Path(path)
        while self._running:
            await asyncio.sleep(self._poll_interval)
            if not base.exists():
                continue
            for entry in base.rglob("*"):
                if not entry.is_file():
                    continue
                stat = entry.stat()
                mtime = stat.st_mtime
                rel = str(entry.relative_to(base))
                prev = self._mtimes.get(rel)
                if prev is not None and mtime != prev:
                    event = {
                        "path": rel,
                        "type": "modified",
                        "timestamp": mtime,
                    }
                    for cb in self._callbacks:
                        cb(event)
                elif prev is None:
                    event = {
                        "path": rel,
                        "type": "created",
                        "timestamp": mtime,
                    }
                    for cb in self._callbacks:
                        cb(event)
                self._mtimes[rel] = mtime
