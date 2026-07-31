"""Comment lifecycle management."""

from __future__ import annotations

from typing import Any

from collaboration.collaboration_models import (CommentRecord, EntityKind)
from collaboration.collaboration_protocols import new_id
from collaboration.comments.comment_moderation import CommentModeration
from collaboration.comments.comment_thread import CommentThread


class CommentManager:
    """CRUD for comments plus threads and moderation."""

    def __init__(self, registry: Any = None,
                 moderation: CommentModeration | None = None) -> None:
        self.registry = registry
        self.moderation = moderation or CommentModeration()
        self.thread = CommentThread()
        self._by_id: dict[str, CommentRecord] = {}
        self._by_target: dict[str, list[str]] = {}

    def add(self, target_kind: EntityKind, target_id: str,
            author_id: str, body: str,
            parent_id: str = "") -> CommentRecord | None:
        result = self.moderation.moderate(body)
        if result["blocked"]:
            return None
        comment = CommentRecord(comment_id=new_id("cmt"),
                                target_kind=target_kind, target_id=target_id,
                                author_id=author_id, body=result["body"])
        self._by_id[comment.comment_id] = comment
        self._by_target.setdefault(target_id, []).append(comment.comment_id)
        if self.registry is not None:
            self.registry.add_comment(comment)
        if parent_id:
            self.thread.add(comment, parent_id)
        return comment

    def get(self, comment_id: str) -> CommentRecord | None:
        return self._by_id.get(comment_id)

    def for_target(self, target_id: str) -> list[CommentRecord]:
        return [self._by_id[cid] for cid in self._by_target.get(target_id, [])
                if cid in self._by_id]

    def replies(self, parent_id: str) -> list[CommentRecord]:
        return [self._by_id[cid] for cid in self.thread.replies(parent_id)
                if cid in self._by_id]

    def remove(self, comment_id: str) -> bool:
        comment = self._by_id.pop(comment_id, None)
        if comment is None:
            return False
        self.thread.remove(comment_id)
        target_ids = self._by_target.get(comment.target_id, [])
        if comment_id in target_ids:
            target_ids.remove(comment_id)
        if self.registry is not None:
            self.registry.remove_comments(comment.target_id)
            for cid in target_ids:
                self.registry.add_comment(self._by_id[cid])
        return True

    def count(self) -> int:
        return len(self._by_id)
