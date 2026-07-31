"""Knowledge Context — Context management for the knowledge platform."""
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class KnowledgeContext:
    context_id: str = ""
    session_id: str = ""
    user_id: str = ""
    current_topic: str = ""
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    active_knowledge: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def add_to_history(self, role: str, content: str) -> None:
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        })

    def set_topic(self, topic: str) -> None:
        self.current_topic = topic

    def add_knowledge_reference(self, knowledge_id: str) -> None:
        if knowledge_id not in self.active_knowledge:
            self.active_knowledge.append(knowledge_id)

    def clear(self) -> None:
        self.conversation_history.clear()
        self.active_knowledge.clear()
        self.current_topic = ""
