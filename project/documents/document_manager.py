from __future__ import annotations

import logging
import uuid
from typing import Any


class Document:
    """Represents a project document."""

    def __init__(self, title: str, project_id: str) -> None:
        self.id = str(uuid.uuid4())
        self.title = title
        self.project_id = project_id
        self.content: str = ""
        self.tags: list[str] = []


class DocumentManager:
    """Manages project documents."""

    def __init__(self) -> None:
        self._documents: dict[str, Document] = {}
        self._log = logging.getLogger("superdev.project.documents")

    def create(self, title: str, project_id: str) -> Document:
        doc = Document(title=title, project_id=project_id)
        self._documents[doc.id] = doc
        return doc

    def get(self, doc_id: str) -> Document | None:
        return self._documents.get(doc_id)

    def update_content(self, doc_id: str, content: str) -> None:
        doc = self._documents.get(doc_id)
        if doc:
            doc.content = content

    def list_by_project(self, project_id: str) -> list[Document]:
        return [d for d in self._documents.values() if d.project_id == project_id]
