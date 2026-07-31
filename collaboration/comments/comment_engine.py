"""Comment engine: discussões colaborativas.

Humanos e agentes de IA comentam tarefas, projetos e documentos.
"""

from __future__ import annotations

from typing import Any

from collaboration.collaboration_config import CollaborationConfig
from collaboration.collaboration_events import (CollaborationEventType,
                                                CollaborationEvents)
from collaboration.collaboration_logger import get_logger
from collaboration.collaboration_metrics import CollaborationMetrics
from collaboration.collaboration_models import (CommentRecord, EntityKind)
from collaboration.collaboration_registry import CollaborationRegistry
from collaboration.collaboration_security import CollaborationSecurity
from collaboration.comments.comment_manager import CommentManager
from collaboration.comments.comment_mentions import (agent_mentions,
                                                     mentions_in)
from collaboration.comments.comment_moderation import CommentModeration


class CommentEngine:
    """Orquestrador de comentários (Fase 5 do Volume 26)."""

    def __init__(self, events: CollaborationEvents | None = None,
                 metrics: CollaborationMetrics | None = None,
                 config: CollaborationConfig | None = None,
                 security: CollaborationSecurity | None = None,
                 registry: CollaborationRegistry | None = None,
                 manager: CommentManager | None = None) -> None:
        self._log = get_logger()
        self.events = events or CollaborationEvents()
        self.metrics = metrics or CollaborationMetrics()
        self.config = config or CollaborationConfig()
        self.security = security or CollaborationSecurity()
        self.manager = manager or CommentManager(registry=registry)

    def add(self, target_kind: EntityKind, target_id: str,
            author_id: str, body: str,
            parent_id: str = "") -> CommentRecord | None:
        comment = self.manager.add(target_kind, target_id, author_id,
                                   body, parent_id)
        if comment is None:
            return None
        self.metrics.increment("collab.comments")
        self.events.publish(CollaborationEventType.COMMENT_ADDED,
                            {"comment_id": comment.comment_id,
                             "target_id": target_id,
                             "author_id": author_id})
        return comment

    def for_target(self, target_id: str) -> list[CommentRecord]:
        return self.manager.for_target(target_id)

    def replies(self, parent_id: str) -> list[CommentRecord]:
        return self.manager.replies(parent_id)

    def get(self, comment_id: str) -> CommentRecord | None:
        return self.manager.get(comment_id)

    def remove(self, comment_id: str) -> bool:
        return self.manager.remove(comment_id)

    def mentions(self, body: str) -> list[str]:
        return mentions_in(body, self.config.mention_prefix)

    def agent_mentions(self, body: str) -> list[str]:
        return agent_mentions(body, self.config.agent_prefix)

    def moderate(self, body: str) -> dict[str, Any]:
        return self.manager.moderation.moderate(body)

    def stats(self) -> dict[str, Any]:
        return {"comments": self.manager.count()}
