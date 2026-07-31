from __future__ import annotations

import logging


class DocFormatter:
    """Formats raw documentation content into structured output formats."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.documentation.formatter")

    def format_markdown(self, content: str) -> str:
        raise NotImplementedError

    def format_rst(self, content: str) -> str:
        raise NotImplementedError

    def format_html(self, content: str) -> str:
        raise NotImplementedError
