from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
import re


@dataclass
class ConversationContext:
    conversation_id: str
    entities: list[str] = field(default_factory=list)
    topics: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)
    turn_count: int = 0
    last_message: str = ""
    started_at: str = ""


class ContextTracker:
    def __init__(self) -> None:
        self._contexts: dict[str, ConversationContext] = {}

    def update_context(self, conversation_id: str, message: str) -> ConversationContext:
        if conversation_id not in self._contexts:
            self._contexts[conversation_id] = ConversationContext(
                conversation_id=conversation_id,
                started_at=datetime.now().isoformat(),
            )

        ctx = self._contexts[conversation_id]
        ctx.turn_count += 1
        ctx.last_message = message

        detected_entities = self._extract_entities(message)
        for ent in detected_entities:
            if ent not in ctx.entities:
                ctx.entities.append(ent)

        new_topic = self._extract_topic(message)
        if new_topic and (not ctx.topics or ctx.topics[-1] != new_topic):
            ctx.topics.append(new_topic)

        ctx.references.append(message[:50])

        return ctx

    def get_context(self, conversation_id: str) -> Optional[ConversationContext]:
        return self._contexts.get(conversation_id)

    def get_entities(self, conversation_id: str) -> list[str]:
        ctx = self._contexts.get(conversation_id)
        return ctx.entities if ctx else []

    def get_current_topic(self, conversation_id: str) -> Optional[str]:
        ctx = self._contexts.get(conversation_id)
        return ctx.topics[-1] if ctx and ctx.topics else None

    def detect_topic_change(self, conversation_id: str, message: str) -> bool:
        ctx = self._contexts.get(conversation_id)
        if not ctx:
            return False
        current_topic = ctx.topics[-1] if ctx.topics else ""
        new_topic = self._extract_topic(message)
        return bool(new_topic) and new_topic != current_topic

    def get_context_summary(self, conversation_id: str) -> dict[str, Any]:
        ctx = self._contexts.get(conversation_id)
        if not ctx:
            return {"error": "Conversation not found"}
        return {
            "conversation_id": ctx.conversation_id,
            "turn_count": ctx.turn_count,
            "entities": ctx.entities,
            "topics": ctx.topics,
            "reference_count": len(ctx.references),
            "last_message_preview": ctx.last_message[:80] if ctx.last_message else "",
            "started_at": ctx.started_at,
        }

    def _extract_entities(self, message: str) -> list[str]:
        words = re.findall(r"[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*", message)
        return [w for w in words if len(w) > 1]

    def _extract_topic(self, message: str) -> Optional[str]:
        stop_words = {"the", "a", "an", "is", "are", "was", "were", "in", "on", "at", "to", "for", "of", "with", "and", "or", "but"}
        words = [w.lower().strip(".,!?;:") for w in message.split() if w.lower().strip(".,!?;:") not in stop_words]
        if words:
            noun_phrases = [w for w in words if len(w) > 2]
            return noun_phrases[0] if noun_phrases else words[0]
        return None
