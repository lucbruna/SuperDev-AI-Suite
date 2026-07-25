from __future__ import annotations as __

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from uuid import uuid4

from pydantic import BaseModel, Field


class LicenseInfo(BaseModel):
    key: str
    type: str = Field(..., pattern=r"^(trial|full|enterprise)$")
    valid_from: datetime
    valid_until: datetime | None = None
    max_users: int = 10
    features: List[str] = Field(default_factory=list)
    issued_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True


class LicenseManager:
    def __init__(self) -> None:
        self._licenses: Dict[str, LicenseInfo] = {}
        self._activations: Dict[str, str] = {}

    async def validate_license(self, license_key: str) -> LicenseInfo | None:
        await asyncio.sleep(0.01)
        return self._licenses.get(license_key)

    async def activate_license(
        self, license_key: str, machine_id: str
    ) -> LicenseInfo:
        await asyncio.sleep(0.01)
        lic = self._licenses.get(license_key)
        if not lic:
            raise ValueError(f"License key not found: {license_key}")
        if not lic.is_active:
            raise ValueError("License is deactivated")
        if lic.valid_until and datetime.utcnow() > lic.valid_until:
            raise ValueError("License has expired")

        self._activations[license_key] = machine_id
        return lic

    async def deactivate_license(self, license_key: str) -> bool:
        await asyncio.sleep(0.01)
        lic = self._licenses.get(license_key)
        if not lic:
            return False
        lic.is_active = False
        self._activations.pop(license_key, None)
        return True

    async def get_license_info(self) -> Dict[str, Any]:
        await asyncio.sleep(0.01)
        return {
            "total_licenses": len(self._licenses),
            "active_licenses": sum(
                1 for l in self._licenses.values() if l.is_active
            ),
            "activations": len(self._activations),
        }

    async def issue_license(
        self,
        license_type: str = "trial",
        max_users: int = 10,
        features: Optional[List[str]] = None,
        valid_days: int = 30,
    ) -> LicenseInfo:
        await asyncio.sleep(0.01)
        features = features or ["basic"]
        now = datetime.utcnow()
        lic = LicenseInfo(
            key=f"lic_{uuid4().hex[:16]}",
            type=license_type,
            valid_from=now,
            valid_until=now + timedelta(days=valid_days),
            max_users=max_users,
            features=features,
        )
        self._licenses[lic.key] = lic
        return lic
