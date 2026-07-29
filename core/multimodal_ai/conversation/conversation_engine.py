from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from .dialogue_manager import DialogueManager
from .context_tracker import ContextTracker
from .memory_linker import MemoryLinker


@dataclass
class EngineConfig:
    max_history: int = 100
    auto_start: bool = True
    default_language: str = "en"
    memory_ttl_seconds: int = 3600


@dataclass
class EngineState:
    running: bool = False
    conversation_id: Optional[str] = None
    started_at: Optional[datetime] = None
    message_count: int = 0


@dataclass
class EngineMetrics:
    total_messages_processed: int = 0
    total_conversations_started: int = 0
    total_conversations_ended: int = 0
    avg_response_time_ms: float = 0.0
    errors: int = 0


class ConversationEngine:
    def __init__(self, config: Optional[EngineConfig] = None) -> None:
        self.config = config or EngineConfig()
        self.state = EngineState()
        self.metrics = EngineMetrics()
        self.dialogue_manager = DialogueManager()
        self.context_tracker = ContextTracker()
        self.memory_linker = MemoryLinker()
        self._conversations: dict[str, list[dict[str, Any]]] = {}

    async def initialize(self) -> None:
        self.state.running = True
        self.state.started_at = datetime.now()

    async def stop(self) -> None:
        self.state.running = False

    async def start_conversation(self) -> str:
        conv_id = str(uuid.uuid4())
        self.state.conversation_id = conv_id
        self._conversations[conv_id] = []
        self.metrics.total_conversations_started += 1
        return conv_id

    async def end_conversation(self, conversation_id: str) -> bool:
        if conversation_id in self._conversations:
            self.dialogue_manager.handle_turn(conversation_id, "__end__", "farewell")
            del self._conversations[conversation_id]
            self.metrics.total_conversations_ended += 1
            if self.state.conversation_id == conversation_id:
                self.state.conversation_id = None
            return True
        return False

    async def process_message(
        self, message: str, conversation_id: Optional[str] = None
    ) -> dict[str, Any]:
        if not self.state.running:
            raise RuntimeError("ConversationEngine is not running")

        conv_id = conversation_id or self.state.conversation_id
        if not conv_id or conv_id not in self._conversations:
            conv_id = await self.start_conversation()

        self.state.message_count += 1
        self.metrics.total_messages_processed += 1

        self.context_tracker.update_context(conv_id, message)
        dialogue_result = self.dialogue_manager.manage_dialogue(message)
        memory = self.memory_linker.retrieve_memory(message)

        response = {
            "conversation_id": conv_id,
            "message": message,
            "dialogue_state": dialogue_result["state"].value,
            "next_action": dialogue_result["next_action"],
            "response_type": dialogue_result["response_type"],
            "context": self.context_tracker.get_context(conv_id),
            "topic": self.context_tracker.get_current_topic(conv_id),
            "relevant_memories": memory,
            "timestamp": datetime.now().isoformat(),
        }

        self._conversations[conv_id].append(
            {"role": "user", "content": message, "timestamp": response["timestamp"]}
        )

        self.memory_linker.store_memory(
            f"msg_{self.metrics.total_messages_processed}",
            message,
            {"conversation_id": conv_id, "dialogue_state": dialogue_result["state"].value},
        )

        return response

    async def get_history(self, conversation_id: str) -> list[dict[str, Any]]:
        return self._conversations.get(conversation_id, [])
