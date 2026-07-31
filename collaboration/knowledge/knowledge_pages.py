"""Wiki pages."""

from __future__ import annotations

from typing import Any

from collaboration.collaboration_models import KnowledgeRecord
from collaboration.collaboration_protocols import new_id


class KnowledgePage:
    """A single wiki page (wraps KnowledgeRecord)."""

    def __init__(self, workspace_id: str, title: str, body: str,
                 author_id: str, tags: list[str]) -> None:
        self.record = KnowledgeRecord(
            document_id=new_id("doc"), workspace_id=workspace_id,
            title=title, body=body, author_id=author_id,
            tags=list(tags or []))

    def edit(self, body: str, editor_id: str,
             tags: list[str] | None = None) -> int:
        """Updates body/tags, bumps version, returns new version."""
        self.record.body = body
        if tags is not None:
            self.record.tags = list(tags)
        self.record.author_id = editor_id
        self.record.version += 1
        return self.record.version

    def to_dict(self) -> dict[str, Any]:
        return {"document_id": self.record.document_id,
                "workspace_id": self.record.workspace_id,
                "title": self.record.title,
                "body": self.record.body,
                "author_id": self.record.author_id,
                "tags": list(self.record.tags),
                "version": self.record.version}
