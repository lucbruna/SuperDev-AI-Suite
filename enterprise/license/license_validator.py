from __future__ import annotations as __

import hashlib
import platform
from datetime import datetime
from typing import Dict, Any, List

from .license_manager import LicenseInfo


class LicenseValidator:
    def check_expiry(self, license: LicenseInfo) -> bool:
        now = datetime.utcnow()
        if license.valid_until and now > license.valid_until:
            return False
        if license.valid_from and now < license.valid_from:
            return False
        return True

    def check_feature(self, license: LicenseInfo, feature: str) -> bool:
        return feature in license.features

    def check_user_count(self, license: LicenseInfo, current_count: int) -> bool:
        return current_count <= license.max_users

    def generate_fingerprint(self) -> str:
        raw = f"{platform.node()}-{platform.machine()}-{platform.processor()}"
        return hashlib.sha256(raw.encode()).hexdigest()[:32]

    def validate_all(
        self,
        license: LicenseInfo,
        current_user_count: int = 0,
        required_features: List[str] | None = None,
    ) -> Dict[str, Any]:
        required_features = required_features or []
        checks = {
            "valid": True,
            "expired": not self.check_expiry(license),
            "exceeded_users": not self.check_user_count(license, current_user_count),
            "missing_features": [
                f for f in required_features if not self.check_feature(license, f)
            ],
        }
        checks["valid"] = not (
            checks["expired"]
            or checks["exceeded_users"]
            or bool(checks["missing_features"])
        )
        return checks
