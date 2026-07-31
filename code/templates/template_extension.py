from __future__ import annotations

from typing import Any


class TemplateExtension:
    """Base class for template engine extensions (filters, globals, tags)."""

    name: str = ""

    def get_filters(self) -> dict[str, Any]:
        return {}

    def get_globals(self) -> dict[str, Any]:
        return {}

    def get_tests(self) -> dict[str, Any]:
        return {}
