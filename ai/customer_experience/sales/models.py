"""Sales intelligence models."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class LeadSource(Enum):
    WEBSITE = "website"
    REFERRAL = "referral"
    COLD_CALL = "cold_call"
    EVENT = "event"
    SOCIAL = "social"
    ORGANIC = "organic"


class SalesStage(Enum):
    QUALIFICATION = "qualification"
    NEEDS_ANALYSIS = "needs_analysis"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


@dataclass
class SalesLead:
    lead_id: str
    customer_id: str = ""
    name: str = ""
    email: str = ""
    source: LeadSource = LeadSource.WEBSITE
    score: float = 0.0
    value: float = 0.0
    stage: SalesStage = SalesStage.QUALIFICATION
    assigned_to: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    last_contact: datetime | None = None

    @property
    def is_qualified(self) -> bool:
        return self.score >= 70


@dataclass
class SalesPrediction:
    prediction_id: str
    lead_id: str = ""
    conversion_probability: float = 0.0
    predicted_value: float = 0.0
    predicted_close_date: datetime | None = None
    confidence: float = 0.0
    factors: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class SalesActivity:
    activity_id: str
    lead_id: str = ""
    activity_type: str = ""
    description: str = ""
    outcome: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
