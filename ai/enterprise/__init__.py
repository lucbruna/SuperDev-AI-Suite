"""SuperDev AI Suite v5 Enterprise - Billing, License & Enterprise Management Engine."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .analytics import (
    BusinessAnalytics,
    BusinessForecasting,
    CustomerAnalytics,
    RetentionAnalytics,
    RevenueAnalytics,
    UsageAnalysis,
)
from .billing import (
    BillingCalculator,
    BillingEngine,
    ChargeManager,
    DiscountManager,
    PricingRules,
    ReconciliationManager,
    TaxManager,
)
from .contracts import (
    AgreementManager,
    ComplianceManager,
    ContractCustomer,
    ContractEngine,
    ContractRenewal,
    SLAManager,
)

# Core infrastructure
from .enterprise_config import (
    BillingConfig,
    BillingCycle,
    EnterpriseConfig,
    EnterpriseLimits,
    LicenseConfig,
    PlanType,
    TenantIsolation,
)
from .enterprise_context import EnterpriseContext
from .enterprise_engine import EnterpriseEngine
from .enterprise_events import EnterpriseEvents
from .enterprise_factory import EnterpriseFactory
from .enterprise_interfaces import (
    BillingInterface,
    LicenseInterface,
    OrganizationInterface,
    SubscriptionInterface,
    UsageInterface,
)
from .enterprise_logger import EnterpriseLogger, LogLevel
from .enterprise_manager import EnterpriseManager
from .enterprise_metrics import EnterpriseMetrics
from .enterprise_models import (
    Contract,
    Invoice,
    License,
    LicenseStatus,
    Organization,
    OrganizationStatus,
    Payment,
    PaymentStatus,
    Subscription,
    SubscriptionStatus,
    UsageRecord,
    User,
    UserStatus,
)
from .enterprise_protocols import Billable, Licensable, Reportable, Subscribable, Trackable
from .enterprise_registry import EnterpriseRegistry
from .enterprise_runtime import EnterpriseRuntime
from .enterprise_security import EnterpriseSecurity
from .invoices import (
    InvoiceCalculator,
    InvoiceDelivery,
    InvoiceEngine,
    InvoiceExporter,
    InvoiceGenerator,
    InvoiceNumbering,
)
from .licenses import (
    LicenseActivation,
    LicenseEngine,
    LicenseExpiration,
    LicenseKeyGenerator,
    LicenseManager,
    LicenseTransfer,
    LicenseValidator,
)
from .limits import LimitAlerts, LimitEnforcer, LimitEngine, LimitPolicies, QuotaManager

# Subsystems
from .organizations import (
    BrandingManager,
    CompanyProfile,
    DepartmentManager,
    MemberManager,
    OrganizationEngine,
    OrganizationHierarchy,
    OrganizationManager,
    OrganizationSettings,
)
from .payments import (
    PaymentAuthorization,
    PaymentEngine,
    PaymentGateway,
    PaymentHistory,
    RefundManager,
    TransactionManager,
    WebhookManager,
)
from .plans import (
    FeatureManager,
    PlanAvailability,
    PlanCatalog,
    PlanComparison,
    PlanEngine,
    PlanManager,
    PricingManager,
)
from .subscriptions import (
    ActivationManager,
    CancellationManager,
    DowngradeManager,
    RenewalManager,
    SubscriptionEngine,
    SubscriptionManager,
    UpgradeManager,
)
from .tenants import TenantConfiguration, TenantDatabase, TenantEngine, TenantIsolation, TenantManager, TenantStorage
from .usage import UsageAnalytics, UsageCounter, UsageEngine, UsageForecasting, UsageQuota, UsageTracker
from .users import (
    InvitationManager,
    UserActivity,
    UserEngine,
    UserManager,
    UserPreferences,
    UserProfile,
    UserStatusManager,
)

__all__ = [
    # Core
    "EnterpriseConfig",
    "EnterpriseEngine",
    "EnterpriseManager",
    "EnterpriseFactory",
    "EnterpriseRegistry",
    "EnterpriseRuntime",
    "EnterpriseContext",
    "EnterpriseEvents",
    "EnterpriseMetrics",
    "EnterpriseLogger",
    "EnterpriseSecurity",
    "LogLevel",
    "PlanType",
    "TenantIsolation",
    "BillingCycle",
    "EnterpriseLimits",
    "BillingConfig",
    "LicenseConfig",
    # Models
    "Organization",
    "OrganizationStatus",
    "User",
    "UserStatus",
    "Subscription",
    "SubscriptionStatus",
    "License",
    "LicenseStatus",
    "Payment",
    "PaymentStatus",
    "Invoice",
    "UsageRecord",
    "Contract",
    # Organizations
    "OrganizationEngine",
    "OrganizationManager",
    "CompanyProfile",
    "OrganizationSettings",
    "OrganizationHierarchy",
    "DepartmentManager",
    "MemberManager",
    "BrandingManager",
    # Users
    "UserEngine",
    "UserManager",
    "UserProfile",
    "InvitationManager",
    "UserStatusManager",
    "UserActivity",
    "UserPreferences",
    # Tenants
    "TenantEngine",
    "TenantManager",
    "TenantConfiguration",
    "TenantStorage",
    "TenantDatabase",
    # Plans
    "PlanEngine",
    "PlanManager",
    "PlanCatalog",
    "FeatureManager",
    "PricingManager",
    "PlanAvailability",
    "PlanComparison",
    # Subscriptions
    "SubscriptionEngine",
    "SubscriptionManager",
    "ActivationManager",
    "RenewalManager",
    "CancellationManager",
    "UpgradeManager",
    "DowngradeManager",
    # Licenses
    "LicenseEngine",
    "LicenseManager",
    "LicenseKeyGenerator",
    "LicenseActivation",
    "LicenseValidator",
    "LicenseExpiration",
    "LicenseTransfer",
    # Billing
    "BillingEngine",
    "BillingCalculator",
    "PricingRules",
    "DiscountManager",
    "TaxManager",
    "ChargeManager",
    "ReconciliationManager",
    # Payments
    "PaymentEngine",
    "PaymentGateway",
    "TransactionManager",
    "PaymentAuthorization",
    "RefundManager",
    "WebhookManager",
    "PaymentHistory",
    # Invoices
    "InvoiceEngine",
    "InvoiceGenerator",
    "InvoiceNumbering",
    "InvoiceCalculator",
    "InvoiceExporter",
    "InvoiceDelivery",
    # Usage
    "UsageEngine",
    "UsageTracker",
    "UsageCounter",
    "UsageAnalytics",
    "UsageQuota",
    "UsageForecasting",
    # Limits
    "LimitEngine",
    "QuotaManager",
    "LimitEnforcer",
    "LimitAlerts",
    "LimitPolicies",
    # Contracts
    "ContractEngine",
    "AgreementManager",
    "ContractCustomer",
    "ContractRenewal",
    "SLAManager",
    "ComplianceManager",
    # Analytics
    "BusinessAnalytics",
    "RevenueAnalytics",
    "CustomerAnalytics",
    "RetentionAnalytics",
    "UsageAnalysis",
    "BusinessForecasting",
]
