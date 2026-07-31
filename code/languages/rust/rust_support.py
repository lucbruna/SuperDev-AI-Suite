from __future__ import annotations

import logging


class RustSupport:
    """Rust language support utilities."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.languages.rust")

    @property
    def extensions(self) -> list[str]:
        return [".rs", ".rlib"]

    def is_rust_file(self, path: str) -> bool:
        return any(path.endswith(ext) for ext in self.extensions)
