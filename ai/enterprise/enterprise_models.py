"""Enterprise data models."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from enum import Enum
from dataclasses import dataclass, field
import time, uuid

class OrganizationStatus(Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"
    PENDING = "pending"

class UserStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"

class SubscriptionStatus(Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PAUSED = "paused"
    PENDING = "pending"

class LicenseStatus(Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    PENDING = "pending"

class PaymentStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

@dataclass
class Organization:
    org_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    slug: str = ""
    status: OrganizationStatus = OrganizationStatus.ACTIVE
    plan: str = "starter"
    created_at: float = field(default_factory=time.time)
    settings: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class User:
    user_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    org_id: str = ""
    email: str = ""
    name: str = ""
    role: str = "member"
    status: UserStatus = UserStatus.ACTIVE
    created_at: float = field(default_factory=time.time)
    last_login: float = 0.0
    preferences: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Subscription:
    subscription_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    org_id: str = ""
    plan_id: str = ""
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE
    start_date: float = field(default_factory=time.time)
    end_date: float = 0.0
    billing_cycle: str = "monthly"
    auto_renew: bool = True

@dataclass
class License:
    license_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    key: str = ""
    org_id: str = ""
    plan_id: str = ""
    status: LicenseStatus = LicenseStatus.ACTIVE
    created_at: float = field(default_factory=time.time)
    expires_at: float = 0.0
    max_activations: int = 1
    activations: int = 0

@dataclass
class Payment:
    payment_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    org_id: str = ""
    amount: float = 0.0
    currency: str = "BRL"
    method: str = "credit_card"
    status: PaymentStatus = PaymentStatus.PENDING
    created_at: float = field(default_factory=time.time)
    processed_at: float = 0.0

@dataclass
class Invoice:
    invoice_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    invoice_number: str = ""
    org_id: str = ""
    amount: float = 0.0
    tax: float = 0.0
    total: float = 0.0
    status: str = "draft"
    created_at: float = field(default_factory=time.time)
    due_date: float = 0.0

@dataclass
class UsageRecord:
    record_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    org_id: str = ""
    metric: str = ""
    quantity: float = 0.0
    unit: str = ""
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Contract:
    contract_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    org_id: str = ""
    title: str = ""
    status: str = "active"
    start_date: float = field(default_factory=time.time)
    end_date: float = 0.0
    terms: Dict[str, Any] = field(default_factory=dict)
    sla: Dict[str, Any] = field(default_factory=dict)
