"""Comments subsystem (Volume 26, Fase 5): discussões colaborativas.

CommentEngine gerencia comentários com threads, respostas, moderação
e menções (incluindo menções a agentes de IA).
"""
from __future__ import annotations

from .comment_engine import CommentEngine
from .comment_manager import CommentManager
from .comment_mentions import agent_mentions, mentions_in
from .comment_moderation import CommentModeration
from .comment_thread import CommentThread

__all__ = [
    "CommentEngine",
    "CommentManager",
    "CommentModeration",
    "CommentThread",
    "agent_mentions",
    "mentions_in",
]
