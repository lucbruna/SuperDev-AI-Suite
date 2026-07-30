from __future__ import annotations

from typing import Any


class PageGenerator:
    """Generates and manages page/route definitions."""

    def __init__(self) -> None:
        self._pages: dict[str, dict[str, Any]] = {}

    def add_page(self, path: str, component: str, layout: str | None = None) -> str:
        self._pages[path] = {
            "path": path,
            "component": component,
            "layout": layout or "default",
        }
        return path

    def get_page(self, path: str) -> dict[str, Any] | None:
        return self._pages.get(path)

    def remove_page(self, path: str) -> bool:
        if path in self._pages:
            del self._pages[path]
            return True
        return False

    def list_pages(self) -> list[dict[str, Any]]:
        return list(self._pages.values())

    @property
    def page_count(self) -> int:
        return len(self._pages)

    def generate_page_code(self, path: str) -> str:
        page = self._pages.get(path)
        if page is None:
            return f"// Page '{path}' not found"
        comp = page["component"]
        return (
            f"import React from 'react';\n"
            f"import {comp} from '../components/{comp}';\n\n"
            f"const {comp}Page: React.FC = () => {{\n"
            f"  return (\n"
            f"    <div className=\"page\">\n"
            f"      <{comp} />\n"
            f"    </div>\n"
            f"  );\n"
            f"}};\n\n"
            f"export default {comp}Page;\n"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "pages": list(self._pages.values()),
            "page_count": self.page_count,
        }
