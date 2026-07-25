"""Spinner formatter for CLI."""

import itertools
import sys
import threading
import time


class Spinner:
    def __init__(self, message: str = "Loading..."):
        self.message = message
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def __enter__(self) -> "Spinner":
        self.start()
        return self

    def __exit__(self, *args) -> None:
        self.stop()

    def start(self) -> None:
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join()
        sys.stdout.write("\r" + " " * (len(self.message) + 10) + "\r")
        sys.stdout.flush()

    def _run(self) -> None:
        for c in itertools.cycle("|/-\\"):
            if self._stop.is_set():
                break
            sys.stdout.write(f"\r{c} {self.message}")
            sys.stdout.flush()
            time.sleep(0.1)
