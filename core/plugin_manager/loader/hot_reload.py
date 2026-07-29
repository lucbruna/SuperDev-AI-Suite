from __future__ import annotations

import os
import threading
import time
from pathlib import Path
from typing import Callable


class HotReloader:
    def __init__(self, poll_interval: float = 1.0) -> None:
        self._poll_interval = poll_interval
        self._watchers: dict[str, tuple[str, float, Callable[[str], None], threading.Thread, threading.Event]] = {}
        self._running = False

    def watch(self, plugin_path: str | Path, callback: Callable[[str], None]) -> None:
        path = Path(plugin_path).resolve()
        if not path.exists():
            raise FileNotFoundError(f"Path not found: {plugin_path}")

        path_str = str(path)
        if path_str in self._watchers:
            raise ValueError(f"Already watching: {plugin_path}")

        last_mtime = self._get_mtime(path)
        stop_event = threading.Event()
        thread = threading.Thread(
            target=self._poll_loop,
            args=(path_str, last_mtime, callback, stop_event),
            daemon=True,
        )
        self._watchers[path_str] = (path_str, last_mtime, callback, thread, stop_event)
        self._running = True
        thread.start()

    def _get_mtime(self, path: Path) -> float:
        if path.is_file():
            return os.path.getmtime(path)
        max_mtime = 0.0
        for root, dirs, files in os.walk(path):
            for f in files:
                fp = os.path.join(root, f)
                mtime = os.path.getmtime(fp)
                if mtime > max_mtime:
                    max_mtime = mtime
        return max_mtime

    def _poll_loop(self, path_str: str, last_mtime: float, callback: Callable[[str], None], stop_event: threading.Event) -> None:
        while not stop_event.is_set():
            time.sleep(self._poll_interval)
            current_mtime = self._get_mtime(Path(path_str))
            if current_mtime > last_mtime:
                last_mtime = current_mtime
                self._watchers[path_str] = (path_str, last_mtime, callback, self._watchers[path_str][3], stop_event)
                callback(path_str)

    def stop(self) -> None:
        for key in list(self._watchers.keys()):
            path_str, last_mtime, callback, thread, stop_event = self._watchers[key]
            stop_event.set()
            thread.join(timeout=2.0)
        self._watchers.clear()
        self._running = False
