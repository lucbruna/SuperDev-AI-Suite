"""Support models."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class TicketStatus(Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING = "waiting"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class EscalationReason(Enum):
    TIMEOUT = "timeout"
    COMPLEXITY = "complexity"
    CUSTOMER_REQUEST = "customer_request"
    SATISFACTION_LOW = "satisfaction_low"


@dataclass
class SupportTicket:
    ticket_id: str
    customer_id: str = ""
    subject: str = ""
    description: str = ""
    status: TicketStatus = TicketStatus.OPEN
    priority: TicketPriority = TicketPriority.MEDIUM
    assigned_to: str = ""
    category: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    resolution: str = ""
    satisfaction_score: float = 0.0


@dataclass
class ChatMessage:
    message_id: str
    session_id: str = ""
    sender: str = ""
    content: str = ""
    is_bot: bool = False
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class KnowledgeArticle:
    article_id: str
    title: str = ""
    content: str = ""
    category: str = ""
    tags: list[str] = field(default_factory=list)
    helpful_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Escalation:
    escalation_id: str
    ticket_id: str = ""
    reason: EscalationReason = EscalationReason.TIMEOUT
    from_agent: str = ""
    to_agent: str = ""
    notes: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
