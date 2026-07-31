"""Licenses subsystem."""
from .activation import LicenseActivation
from .expiration import LicenseExpiration
from .key_generator import LicenseKeyGenerator
from .license_engine import LicenseEngine
from .license_manager import LicenseManager
from .transfer import LicenseTransfer
from .validation import LicenseValidator

__all__ = [
    "LicenseEngine", "LicenseManager", "LicenseKeyGenerator",
    "LicenseActivation", "LicenseValidator", "LicenseExpiration", "LicenseTransfer"
]
