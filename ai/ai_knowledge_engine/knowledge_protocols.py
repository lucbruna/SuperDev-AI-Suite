"""Knowledge Engine Protocols — Protocol definitions for the knowledge platform."""
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime


class ProtocolType(Enum):
    RESEARCH = "research"
    DOCUMENT_PROCESSING = "document_processing"
    KNOWLEDGE_STORAGE = "knowledge_storage"
    VALIDATION = "validation"
    LEARNING = "learning"
    EMBEDDING = "embedding"
    QUERY = "query"


@dataclass
class ProtocolMessage:
    message_id: str = ""
    protocol_type: ProtocolType = ProtocolType.QUERY
    sender: str = ""
    receiver: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class KnowledgeProtocol:
    def __init__(self):
        self._handlers: Dict[ProtocolType, List[callable]] = {}

    def register_handler(self, protocol_type: ProtocolType, handler: callable) -> None:
        if protocol_type not in self._handlers:
            self._handlers[protocol_type] = []
        self._handlers[protocol_type].append(handler)

    def send(self, message: ProtocolMessage) -> List[Any]:
        handlers = self._handlers.get(message.protocol_type, [])
        results = []
        for handler in handlers:
            result = handler(message)
            results.append(result)
        return results

    def broadcast(self, message: ProtocolMessage) -> List[Any]:
        all_results = []
        for protocol_type in self._handlers:
            msg = ProtocolMessage(
                message_id=message.message_id,
                protocol_type=protocol_type,
                sender=message.sender,
                receiver=message.receiver,
                payload=message.payload,
            )
            all_results.extend(self.send(msg))
        return all_results
