from __future__ import annotations

import logging
from typing import Any


class FileExplorer:
    """Virtual file tree for the editor sidebar."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.editor.explorer")
        self._files: dict[str, str] = {}

    def render(self) -> dict[str, Any]:
        return {"tree": self.tree(""), "count": len(self._files)}

    def tree(self, root: str) -> dict[str, Any]:
        tree: dict[str, Any] = {}
        for path in self._files:
            if not path.startswith(root):
                continue
            rel = path[len(root):].strip("/")
            if not rel:
                continue
            parts = rel.split("/")
            node = tree
            for part in parts[:-1]:
                node = node.setdefault(part, {})
            node[parts[-1]] = self._files[path]
        return tree

    def search(self, query: str) -> list[dict[str, Any]]:
        return [
            {"path": path, "content": content}
            for path, content in self._files.items()
            if query.lower() in path.lower()
        ]

    def create(self, path: str, content: str = "") -> bool:
        if path in self._files:
            return False
        self._files[path] = content
        return True
