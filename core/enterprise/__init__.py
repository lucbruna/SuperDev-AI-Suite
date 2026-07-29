try:
    from enterprise.billing.subscription_manager import SubscriptionManager  # type: ignore
except ImportError:
    SubscriptionManager = None  # type: ignore

try:
    from enterprise.multi_tenancy.tenant_manager import TenantManager  # type: ignore
except ImportError:
    TenantManager = None  # type: ignore

try:
    from enterprise.sso.sso_handler import SSOHandler  # type: ignore
except ImportError:
    SSOHandler = None  # type: ignore

try:
    from enterprise.feature_flags.flag_manager import FeatureFlagManager  # type: ignore
except ImportError:
    FeatureFlagManager = None  # type: ignore

__all__ = ["SubscriptionManager", "TenantManager", "SSOHandler", "FeatureFlagManager"]