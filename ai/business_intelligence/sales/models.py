"""Sales models."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class DealStage(Enum):
    LEAD = "lead"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


class LeadSource(Enum):
    WEBSITE = "website"
    REFERRAL = "referral"
    COLD_CALL = "cold_call"
    EVENT = "event"
    ORGANIC = "organic"
    PAID = "paid"


@dataclass
class Deal:
    deal_id: str
    title: str
    value: float
    stage: DealStage = DealStage.LEAD
    owner: str = ""
    company: str = ""
    close_date: datetime | None = None
    created_at: datetime = field(default_factory=datetime.now)
    probability: float = 0.0
    contacts: list[str] = field(default_factory=list)
    notes: str = ""

    @property
    def weighted_value(self) -> float:
        return self.value * (self.probability / 100)

    @property
    def is_won(self) -> bool:
        return self.stage == DealStage.CLOSED_WON

    @property
    def is_lost(self) -> bool:
        return self.stage == DealStage.CLOSED_LOST


@dataclass
class Contact:
    contact_id: str
    name: str
    email: str = ""
    phone: str = ""
    company: str = ""
    title: str = ""
    lead_source: LeadSource = LeadSource.WEBSITE
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Activity:
    activity_id: str
    deal_id: str
    activity_type: str = "call"
    description: str = ""
    duration_minutes: int = 0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class SalesMetrics:
    pipeline_value: float = 0.0
    won_value: float = 0.0
    lost_value: float = 0.0
    win_rate: float = 0.0
    avg_deal_size: float = 0.0
    avg_sales_cycle_days: float = 0.0
    total_deals: int = 0
    activities_count: int = 0
    forecast_value: float = 0.0
