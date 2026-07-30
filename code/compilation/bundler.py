from __future__ import annotations

import logging
from typing import Any


class Bundler:
    """Bundles multiple source files into a single output."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.compilation.bundler")

    def bundle(self, files: list[str], output: str, format: str = "esm") -> dict[str, Any]:
        self._log.info("Bundling %d files into %s (%s)", len(files), output, format)
        return {"success": True, "output": output, "size": 0}

    def watch(self, files: list[str], output: str) -> None:
        self._log.info("Watching %d files for changes", len(files))
