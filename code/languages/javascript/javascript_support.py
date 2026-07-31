from __future__ import annotations

import logging


class JavaScriptSupport:
    """JavaScript language support utilities."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.languages.javascript")

    @property
    def extensions(self) -> list[str]:
        return [".js", ".jsx", ".mjs", ".cjs"]

    def is_js_file(self, path: str) -> bool:
        return any(path.endswith(ext) for ext in self.extensions)
