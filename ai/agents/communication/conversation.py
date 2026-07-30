from __future__ import annotations

from typing import Any, Dict, List, Optional


class Conversation:
    """Represents a conversation between agents."""

    def __init__(self, conversation_id: str, participants: List[str]) -> None:
        self._conversation_id = conversation_id
        self._participants = participants
        self._messages: List[Dict[str, Any]] = []

    @property
    def conversation_id(self) -> str:
        return self._conversation_id

    @property
    def participants(self) -> List[str]:
        return list(self._participants)

    @property
    def messages(self) -> List[Dict[str, Any]]:
        return list(self._messages)

    def add_message(self, sender: str, content: Dict[str, Any]) -> None:
        self._messages.append({"sender": sender, "content": content})

    def last_message(self) -> Optional[Dict[str, Any]]:
        return self._messages[-1] if self._messages else None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "conversation_id": self._conversation_id,
            "participants": self._participants,
            "message_count": len(self._messages),
        }
