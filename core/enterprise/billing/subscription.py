from __future__ import annotations as __

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import uuid4

from pydantic import BaseModel, Field


class SubscriptionPlan(BaseModel):
    tier: str = Field(..., pattern=r"^(free|starter|pro|enterprise)$")
    label: str = ""


class Subscription(BaseModel):
    id: str = Field(default_factory=lambda: f"sub_{uuid4().hex[:12]}")
    org_id: str
    plan: SubscriptionPlan
    status: str = Field(
        default="trialing", pattern=r"^(active|canceled|past_due|trialing)$"
    )
    current_period_start: datetime = Field(default_factory=datetime.utcnow)
    current_period_end: datetime | None = None
    features: List[str] = Field(default_factory=list)
    limits: Dict[str, int] = Field(default_factory=dict)
    trial_end: datetime | None = None
    canceled_at: datetime | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def is_active(self) -> bool:
        return self.status in ("active", "trialing")

    def is_trialing(self) -> bool:
        return self.status == "trialing"

    def cancel(self) -> None:
        self.status = "canceled"
        self.canceled_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def mark_past_due(self) -> None:
        self.status = "past_due"
        self.updated_at = datetime.utcnow()

    def activate(self) -> None:
        self.status = "active"
        self.updated_at = datetime.utcnow()

    def change_plan(self, new_tier: str) -> None:
        self.plan = SubscriptionPlan(tier=new_tier)
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
