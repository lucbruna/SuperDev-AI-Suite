from __future__ import annotations

import logging
from pathlib import Path
from typing import Any


class TemplateEngine:
    """Central template engine for code generation."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.templates")
        self._loader: TemplateLoader | None = None
        self._cache: TemplateCache | None = None
        self._compiler: TemplateCompiler | None = None
        self._extensions: list[TemplateExtension] = []

    def render(self, name: str, context: dict[str, Any] | None = None) -> str:
        raise NotImplementedError

    def render_string(self, source: str, context: dict[str, Any] | None = None) -> str:
        raise NotImplementedError

    def register_extension(self, ext: TemplateExtension) -> None:
        self._extensions.append(ext)

    def clear_cache(self) -> None:
        if self._cache:
            self._cache.clear()
