"""CRM models."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum


class ContactType(Enum):
    PRIMARY = "primary"
    BILLING = "billing"
    TECHNICAL = "technical"
    DECISION_MAKER = "decision_maker"


class OpportunityStage(Enum):
    PROSPECTING = "prospecting"
    QUALIFICATION = "qualification"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


class ActivityType(Enum):
    CALL = "call"
    EMAIL = "email"
    MEETING = "meeting"
    NOTE = "note"
    TASK = "task"


@dataclass
class Account:
    account_id: str
    name: str
    industry: str = ""
    size: str = ""
    website: str = ""
    revenue: float = 0.0
    employees: int = 0
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Contact:
    contact_id: str
    account_id: str = ""
    name: str = ""
    email: str = ""
    phone: str = ""
    contact_type: ContactType = ContactType.PRIMARY
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Opportunity:
    opportunity_id: str
    account_id: str = ""
    name: str = ""
    value: float = 0.0
    stage: OpportunityStage = OpportunityStage.PROSPECTING
    probability: float = 0.0
    close_date: Optional[datetime] = None
    owner: str = ""
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def weighted_value(self) -> float:
        return self.value * (self.probability / 100)


@dataclass
class Activity:
    activity_id: str
    customer_id: str = ""
    activity_type: ActivityType = ActivityType.CALL
    subject: str = ""
    description: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    completed: bool = False
    owner: str = ""
