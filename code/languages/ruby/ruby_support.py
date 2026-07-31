from __future__ import annotations

import logging


class RubySupport:
    """Ruby language support utilities."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.languages.ruby")

    @property
    def extensions(self) -> list[str]:
        return [".rb", ".erb"]

    def is_ruby_file(self, path: str) -> bool:
        return any(path.endswith(ext) for ext in self.extensions)
