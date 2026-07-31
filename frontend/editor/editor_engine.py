from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from .autocomplete import AutocompleteEngine
from .diff_viewer import DiffViewer
from .syntax_highlighter import SyntaxHighlighter


@dataclass
class OpenDocument:
    """State of an open document in the editor."""

    path: str
    language: str = "text"
    content: str = ""
    cursor: int = 0
    dirty: bool = False
    selection: tuple[int, int] | None = None


class EditorEngine:
    """Core code editor engine with document management."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.editor")
        self._documents: dict[str, OpenDocument] = {}
        self._active: str | None = None
        self.highlighter = SyntaxHighlighter()
        self.autocomplete = AutocompleteEngine()
        self.diff = DiffViewer()

    def open(self, path: str, content: str = "", language: str | None = None) -> OpenDocument:
        resolved_language: str
        if language is None:
            resolved_language = self.highlighter.language_for_path(path)
        else:
            resolved_language = language
        document = OpenDocument(path=path, content=content, language=resolved_language)
        self._documents[path] = document
        self._active = path
        return document

    def close(self, path: str) -> bool:
        if self._active == path:
            self._active = None
        return self._documents.pop(path, None) is not None

    def active(self) -> OpenDocument | None:
        if self._active is None:
            return None
        return self._documents.get(self._active)

    def set_active(self, path: str) -> None:
        if path not in self._documents:
            raise KeyError(f"document not open: {path}")
        self._active = path

    def update(self, path: str, content: str) -> None:
        document = self._documents[path]
        document.content = content
        document.dirty = True

    def save(self, path: str) -> None:
        if path in self._documents:
            self._documents[path].dirty = False

    def open_documents(self) -> list[dict[str, Any]]:
        return [vars(doc) for doc in self._documents.values()]

    def highlight(self, path: str) -> list[dict[str, Any]]:
        document = self._documents.get(path)
        if document is None:
            return []
        return self.highlighter.tokenize(document.content, document.language)

    def suggest(self, path: str, prefix: str) -> list[str]:
        document = self._documents.get(path)
        language = document.language if document else "text"
        return self.autocomplete.suggest(prefix, language)
