"""Enterprise configuration."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class PlanType(Enum):
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"

class TenantIsolation(Enum):
    SHARED = "shared"
    DEDICATED = "dedicated"
    ISOLATED = "isolated"

class BillingCycle(Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"

@dataclass
class EnterpriseLimits:
    max_organizations: int = 1000
    max_users_per_org: int = 10000
    max_agents: int = 100
    max_projects: int = 1000
    max_storage_gb: int = 1000
    max_api_calls: int = 1000000
    max_tokens_monthly: int = 10000000

@dataclass
class BillingConfig:
    currency: str = "BRL"
    tax_rate: float = 0.0
    late_fee_rate: float = 0.02
    grace_period_days: int = 7
    auto_charge: bool = True
    invoice_prefix: str = "INV"
    payment_methods: list[str] = field(default_factory=lambda: ["credit_card", "pix", "boleto"])

@dataclass
class LicenseConfig:
    key_prefix: str = "SD"
    key_length: int = 32
    max_activations: int = 1
    allow_transfer: bool = False
    expiration_enabled: bool = True

@dataclass
class EnterpriseConfig:
    limits: EnterpriseLimits = field(default_factory=EnterpriseLimits)
    billing: BillingConfig = field(default_factory=BillingConfig)
    license: LicenseConfig = field(default_factory=LicenseConfig)
    tenant_isolation: TenantIsolation = TenantIsolation.SHARED
    default_plan: PlanType = PlanType.STARTER
    trial_days: int = 14
    enabled: bool = True
    debug_mode: bool = False
