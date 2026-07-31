"""Comment threads and replies."""

from __future__ import annotations

from typing import Any

from collaboration.collaboration_models import CommentRecord


class CommentThread:
    """Groups comments by parent/child relationship."""

    def __init__(self) -> None:
        self._children: dict[str, list[str]] = {}

    def add(self, comment: CommentRecord, parent_id: str = "") -> None:
        if parent_id:
            self._children.setdefault(parent_id, [])
            if comment.comment_id not in self._children[parent_id]:
                self._children[parent_id].append(comment.comment_id)

    def replies(self, parent_id: str) -> list[str]:
        return list(self._children.get(parent_id, []))

    def reply_count(self, parent_id: str) -> int:
        return len(self._children.get(parent_id, []))

    def has_children(self, comment_id: str) -> bool:
        return bool(self._children.get(comment_id))

    def remove(self, comment_id: str) -> None:
        self._children.pop(comment_id, None)
        for values in self._children.values():
            if comment_id in values:
                values.remove(comment_id)

    def to_dict(self) -> dict[str, Any]:
        return {k: list(v) for k, v in self._children.items()}
