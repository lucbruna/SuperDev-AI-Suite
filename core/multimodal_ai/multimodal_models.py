"""
Multimodal Models - Data models for multimodal AI interactions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class InputType(Enum):
    TEXT = "text"
    VOICE = "voice"
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"
    SENSOR = "sensor"


class OutputType(Enum):
    TEXT = "text"
    VOICE = "voice"
    IMAGE_DESCRIPTION = "image_description"
    DOCUMENT_SUMMARY = "document_summary"
    STRUCTURED_DATA = "structured_data"
    COMMAND = "command"
    MULTIMODAL = "multimodal"


class ModalityType(Enum):
    TEXT = "text"
    VOICE = "voice"
    VISION = "vision"
    VIDEO = "video"
    DOCUMENT = "document"
    SENSOR = "sensor"
    CONVERSATION = "conversation"
    TRANSLATION = "translation"


class InteractionStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class MultimodalInput:
    id: str
    type: InputType
    data: Any
    source: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    language: Optional[str] = None
    raw_bytes: Optional[bytes] = None
    mime_type: Optional[str] = None


@dataclass
class MultimodalOutput:
    id: str
    input_id: str
    type: OutputType
    content: Any
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    alternative_modalities: List[OutputType] = field(default_factory=list)
    processing_time_ms: float = 0.0


@dataclass
class ProcessedInput:
    input_id: str
    original_type: InputType
    normalized_text: Optional[str] = None
    tokens: List[str] = field(default_factory=list)
    embeddings: Optional[List[float]] = None
    features: Dict[str, Any] = field(default_factory=dict)
    detected_language: Optional[str] = None
    confidence: float = 0.0
    processing_time_ms: float = 0.0
    raw_output: Optional[Any] = None


@dataclass
class UnderstandingResult:
    input_id: str
    intent: str = ""
    entities: Dict[str, Any] = field(default_factory=dict)
    sentiment: Optional[float] = None
    topics: List[str] = field(default_factory=list)
    summary: Optional[str] = None
    confidence: float = 0.0
    requires_clarification: bool = False
    suggested_actions: List[str] = field(default_factory=list)
    cross_modality_refs: Dict[str, str] = field(default_factory=dict)


@dataclass
class ResponsePlan:
    id: str
    input_id: str
    primary_output: OutputType
    content: Any = None
    alternatives: List[OutputType] = field(default_factory=list)
    priority: int = 0
    ttl_seconds: int = 60
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InteractionSession:
    id: str
    user_id: Optional[str] = None
    status: InteractionStatus = InteractionStatus.PENDING
    inputs: List[MultimodalInput] = field(default_factory=list)
    outputs: List[MultimodalOutput] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    modality_counts: Dict[str, int] = field(default_factory=dict)
    linked_session_ids: List[str] = field(default_factory=list)

    def add_input(self, inp: MultimodalInput) -> None:
        self.inputs.append(inp)
        self.modality_counts[inp.type.value] = self.modality_counts.get(inp.type.value, 0) + 1
        self.updated_at = datetime.utcnow()

    def add_output(self, out: MultimodalOutput) -> None:
        self.outputs.append(out)
        self.updated_at = datetime.utcnow()

    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
