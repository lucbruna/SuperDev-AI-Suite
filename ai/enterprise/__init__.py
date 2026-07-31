"""SuperDev AI Suite v5 Enterprise - Billing, License & Enterprise Management Engine."""
from __future__ import annotations
from typing import Any, Dict, List, Optional

# Core infrastructure
from .enterprise_config import EnterpriseConfig, PlanType, TenantIsolation, BillingCycle, EnterpriseLimits, BillingConfig, LicenseConfig
from .enterprise_models import (
    Organization, OrganizationStatus, User, UserStatus, Subscription, SubscriptionStatus,
    License, LicenseStatus, Payment, PaymentStatus, Invoice, UsageRecord, Contract
)
from .enterprise_events import EnterpriseEvents
from .enterprise_metrics import EnterpriseMetrics
from .enterprise_logger import EnterpriseLogger, LogLevel
from .enterprise_security import EnterpriseSecurity
from .enterprise_interfaces import OrganizationInterface, BillingInterface, LicenseInterface, UsageInterface, SubscriptionInterface
from .enterprise_protocols import Billable, Subscribable, Licensable, Trackable, Reportable
from .enterprise_context import EnterpriseContext
from .enterprise_registry import EnterpriseRegistry
from .enterprise_runtime import EnterpriseRuntime
from .enterprise_factory import EnterpriseFactory
from .enterprise_manager import EnterpriseManager
from .enterprise_engine import EnterpriseEngine

# Subsystems
from .organizations import (
    OrganizationEngine, OrganizationManager, CompanyProfile,
    OrganizationSettings, OrganizationHierarchy, DepartmentManager,
    MemberManager, BrandingManager
)
from .users import (
    UserEngine, UserManager, UserProfile, InvitationManager,
    UserStatusManager, UserActivity, UserPreferences
)
from .tenants import (
    TenantEngine, TenantManager, TenantIsolation,
    TenantConfiguration, TenantStorage, TenantDatabase
)
from .plans import (
    PlanEngine, PlanManager, PlanCatalog, FeatureManager,
    PricingManager, PlanAvailability, PlanComparison
)
from .subscriptions import (
    SubscriptionEngine, SubscriptionManager, ActivationManager,
    RenewalManager, CancellationManager, UpgradeManager, DowngradeManager
)
from .licenses import (
    LicenseEngine, LicenseManager, LicenseKeyGenerator,
    LicenseActivation, LicenseValidator, LicenseExpiration, LicenseTransfer
)
from .billing import (
    BillingEngine, BillingCalculator, PricingRules,
    DiscountManager, TaxManager, ChargeManager, ReconciliationManager
)
from .payments import (
    PaymentEngine, PaymentGateway, TransactionManager,
    PaymentAuthorization, RefundManager, WebhookManager, PaymentHistory
)
from .invoices import (
    InvoiceEngine, InvoiceGenerator, InvoiceNumbering,
    InvoiceCalculator, InvoiceExporter, InvoiceDelivery
)
from .usage import (
    UsageEngine, UsageTracker, UsageCounter,
    UsageAnalytics, UsageQuota, UsageForecasting
)
from .limits import (
    LimitEngine, QuotaManager, LimitEnforcer, LimitAlerts, LimitPolicies
)
from .contracts import (
    ContractEngine, AgreementManager, ContractCustomer,
    ContractRenewal, SLAManager, ComplianceManager
)
from .analytics import (
    BusinessAnalytics, RevenueAnalytics, CustomerAnalytics,
    RetentionAnalytics, UsageAnalysis, BusinessForecasting
)

__all__ = [
    # Core
    "EnterpriseConfig", "EnterpriseEngine", "EnterpriseManager", "EnterpriseFactory",
    "EnterpriseRegistry", "EnterpriseRuntime", "EnterpriseContext", "EnterpriseEvents",
    "EnterpriseMetrics", "EnterpriseLogger", "EnterpriseSecurity", "LogLevel",
    "PlanType", "TenantIsolation", "BillingCycle", "EnterpriseLimits", "BillingConfig", "LicenseConfig",
    # Models
    "Organization", "OrganizationStatus", "User", "UserStatus",
    "Subscription", "SubscriptionStatus", "License", "LicenseStatus",
    "Payment", "PaymentStatus", "Invoice", "UsageRecord", "Contract",
    # Organizations
    "OrganizationEngine", "OrganizationManager", "CompanyProfile",
    "OrganizationSettings", "OrganizationHierarchy", "DepartmentManager",
    "MemberManager", "BrandingManager",
    # Users
    "UserEngine", "UserManager", "UserProfile", "InvitationManager",
    "UserStatusManager", "UserActivity", "UserPreferences",
    # Tenants
    "TenantEngine", "TenantManager", "TenantConfiguration",
    "TenantStorage", "TenantDatabase",
    # Plans
    "PlanEngine", "PlanManager", "PlanCatalog", "FeatureManager",
    "PricingManager", "PlanAvailability", "PlanComparison",
    # Subscriptions
    "SubscriptionEngine", "SubscriptionManager", "ActivationManager",
    "RenewalManager", "CancellationManager", "UpgradeManager", "DowngradeManager",
    # Licenses
    "LicenseEngine", "LicenseManager", "LicenseKeyGenerator",
    "LicenseActivation", "LicenseValidator", "LicenseExpiration", "LicenseTransfer",
    # Billing
    "BillingEngine", "BillingCalculator", "PricingRules",
    "DiscountManager", "TaxManager", "ChargeManager", "ReconciliationManager",
    # Payments
    "PaymentEngine", "PaymentGateway", "TransactionManager",
    "PaymentAuthorization", "RefundManager", "WebhookManager", "PaymentHistory",
    # Invoices
    "InvoiceEngine", "InvoiceGenerator", "InvoiceNumbering",
    "InvoiceCalculator", "InvoiceExporter", "InvoiceDelivery",
    # Usage
    "UsageEngine", "UsageTracker", "UsageCounter",
    "UsageAnalytics", "UsageQuota", "UsageForecasting",
    # Limits
    "LimitEngine", "QuotaManager", "LimitEnforcer", "LimitAlerts", "LimitPolicies",
    # Contracts
    "ContractEngine", "AgreementManager", "ContractCustomer",
    "ContractRenewal", "SLAManager", "ComplianceManager",
    # Analytics
    "BusinessAnalytics", "RevenueAnalytics", "CustomerAnalytics",
    "RetentionAnalytics", "UsageAnalysis", "BusinessForecasting",
]
